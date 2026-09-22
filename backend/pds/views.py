"""
pds/views.py — PDS ViewSets for all CS Form 212 sections + PDF Export
"""
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.template.loader import render_to_string
import io

from .models import (
    Teacher, PersonalInfo, FamilyBackground, ChildInfo,
    EducationalBackground, CivilServiceEligibility, WorkExperience,
    LearningDevelopment, VoluntaryWork, OtherInformation,
    GovernmentQuestions, Reference, PDSDeclaration,
)
from .serializers import (
    TeacherListSerializer, TeacherCreateSerializer, TeacherUpdateSerializer,
    PersonalInfoSerializer, FamilyBackgroundSerializer,
    EducationalBackgroundSerializer, CivilServiceEligibilitySerializer,
    WorkExperienceSerializer, LearningDevelopmentSerializer,
    VoluntaryWorkSerializer, OtherInformationSerializer,
    GovernmentQuestionsSerializer, ReferenceSerializer,
    PDSDeclarationSerializer, PDSSummarySerializer,
)
from accounts.permissions import IsHROrAdmin, IsOwnerOrHROrAdmin
from django.contrib.auth import get_user_model

User = get_user_model()


# ── Helpers ───────────────────────────────────────────────────────────────────

def get_teacher_for_user(request, teacher_pk):
    """Returns teacher if user is owner or HR/Admin."""
    teacher = get_object_or_404(Teacher, pk=teacher_pk)
    if request.user.role in ('admin', 'hr'):
        return teacher
    if hasattr(request.user, 'teacher_profile') and request.user.teacher_profile == teacher:
        return teacher
    return None


# ── Teacher ViewSet ───────────────────────────────────────────────────────────

class TeacherViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'employee_id', 'department']
    ordering_fields = ['user__last_name', 'department', 'created_at']

    def get_queryset(self):
        user = self.request.user
        if user.role in ('admin', 'hr'):
            qs = Teacher.objects.select_related('user').all()
        else:
            qs = Teacher.objects.filter(user=user)

        # Filters
        dept = self.request.query_params.get('department')
        pds_complete = self.request.query_params.get('pds_complete')
        if dept:
            qs = qs.filter(department__icontains=dept)
        if pds_complete is not None:
            qs = qs.filter(pds_complete=(pds_complete.lower() == 'true'))
        return qs.order_by('user__last_name', 'user__first_name')

    def get_serializer_class(self):
        if self.action == 'create':
            return TeacherCreateSerializer
        if self.action in ('update', 'partial_update'):
            return TeacherUpdateSerializer
        if self.action == 'pds_summary':
            return PDSSummarySerializer
        return TeacherListSerializer

    def get_permissions(self):
        if self.action in ('create', 'destroy'):
            return [IsHROrAdmin()]
        return [IsOwnerOrHROrAdmin()]

    @action(detail=False, methods=['get'], url_path='my-profile')
    def my_profile(self, request):
        if not hasattr(request.user, 'teacher_profile'):
            return Response({'error': 'No teacher profile found for this user.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = PDSSummarySerializer(request.user.teacher_profile, context={'request': request})
        return Response(serializer.data)


    def create(self, request, *args, **kwargs):
        """Create teacher profile. Requires user_id in body."""
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({'error': 'user_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(pk=user_id, role='teacher')
        except User.DoesNotExist:
            return Response({'error': 'Teacher user not found.'}, status=status.HTTP_404_NOT_FOUND)
        if hasattr(user, 'teacher_profile'):
            return Response({'error': 'Teacher profile already exists for this user.'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        teacher = serializer.save(user=user)
        teacher.check_pds_completeness()
        return Response(TeacherListSerializer(teacher, context={'request': request}).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'], url_path='pds-summary')
    def pds_summary(self, request, pk=None):
        teacher = self.get_object()
        serializer = PDSSummarySerializer(teacher, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='export-pdf')
    def export_pdf(self, request, pk=None):
        teacher = get_object_or_404(Teacher.objects.select_related('user'), pk=pk)
        if request.user.role not in ('admin', 'hr'):
            if not hasattr(request.user, 'teacher_profile') or request.user.teacher_profile.pk != teacher.pk:
                return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

        context = {
            'teacher': teacher,
            'personal_info': getattr(teacher, 'personal_info', None),
            'family_background': getattr(teacher, 'family_background', None),
            'educational_backgrounds': teacher.educational_backgrounds.all(),
            'civil_service_eligibilities': teacher.civil_service_eligibilities.all(),
            'work_experiences': teacher.work_experiences.all(),
            'learning_developments': teacher.learning_developments.all(),
            'voluntary_works': teacher.voluntary_works.all(),
            'other_information': getattr(teacher, 'other_information', None),
            'government_questions': getattr(teacher, 'government_questions', None),
            'references': teacher.references.all(),
            'pds_declaration': getattr(teacher, 'pds_declaration', None),
        }
        html_string = render_to_string('pds/pds_export.html', context)
        try:
            import weasyprint
            pdf = weasyprint.HTML(string=html_string, base_url=request.build_absolute_uri('/')).write_pdf()
            response = HttpResponse(pdf, content_type='application/pdf')
            name = teacher.user.get_full_name().replace(',', '').replace(' ', '_')
            response['Content-Disposition'] = f'attachment; filename="PDS_{name}.pdf"'
            return response
        except Exception as e:
            return Response({'error': f'PDF generation failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ── Section ViewBase ─────────────────────────────────────────────────────────

class SectionBaseView(APIView):
    permission_classes = [IsOwnerOrHROrAdmin]
    model_class = None
    serializer_class = None
    related_name = None

    def get_teacher(self, pk):
        return get_object_or_404(Teacher, pk=pk)

    def check_teacher_permission(self, request, teacher):
        if request.user.role in ('admin', 'hr'):
            return True
        return hasattr(request.user, 'teacher_profile') and request.user.teacher_profile == teacher

    def get(self, request, teacher_pk):
        teacher = self.get_teacher(teacher_pk)
        if not self.check_teacher_permission(request, teacher):
            return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
        try:
            instance = getattr(teacher, self.related_name)
            serializer = self.serializer_class(instance)
            return Response(serializer.data)
        except self.model_class.DoesNotExist:
            return Response({}, status=status.HTTP_200_OK)

    def put(self, request, teacher_pk):
        teacher = self.get_teacher(teacher_pk)
        if not self.check_teacher_permission(request, teacher):
            return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
        try:
            instance = getattr(teacher, self.related_name)
            serializer = self.serializer_class(instance, data=request.data, partial=True)
        except self.model_class.DoesNotExist:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save(teacher=teacher)
                teacher.check_pds_completeness()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        teacher.check_pds_completeness()
        return Response(serializer.data)


class ListSectionBaseView(APIView):
    """For 1-to-many sections: Education, Work, L&D, Voluntary, CSE, References."""
    permission_classes = [IsOwnerOrHROrAdmin]
    model_class = None
    serializer_class = None
    related_name = None

    def get_teacher(self, pk):
        return get_object_or_404(Teacher, pk=pk)

    def check_permission(self, request, teacher):
        if request.user.role in ('admin', 'hr'):
            return True
        return hasattr(request.user, 'teacher_profile') and request.user.teacher_profile == teacher

    def get(self, request, teacher_pk):
        teacher = self.get_teacher(teacher_pk)
        if not self.check_permission(request, teacher):
            return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
        qs = getattr(teacher, self.related_name).all()
        serializer = self.serializer_class(qs, many=True)
        return Response(serializer.data)

    def post(self, request, teacher_pk):
        teacher = self.get_teacher(teacher_pk)
        if not self.check_permission(request, teacher):
            return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(teacher=teacher)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ListSectionDetailView(APIView):
    permission_classes = [IsOwnerOrHROrAdmin]
    model_class = None
    serializer_class = None

    def get_object(self, teacher_pk, pk):
        return get_object_or_404(self.model_class, pk=pk, teacher__pk=teacher_pk)

    def check_permission(self, request, obj):
        if request.user.role in ('admin', 'hr'):
            return True
        return hasattr(request.user, 'teacher_profile') and request.user.teacher_profile == obj.teacher

    def get(self, request, teacher_pk, pk):
        obj = self.get_object(teacher_pk, pk)
        if not self.check_permission(request, obj):
            return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
        return Response(self.serializer_class(obj).data)

    def put(self, request, teacher_pk, pk):
        obj = self.get_object(teacher_pk, pk)
        if not self.check_permission(request, obj):
            return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = self.serializer_class(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, teacher_pk, pk):
        obj = self.get_object(teacher_pk, pk)
        if not self.check_permission(request, obj):
            return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ── Concrete Section Views ────────────────────────────────────────────────────

class PersonalInfoView(SectionBaseView):
    model_class = PersonalInfo
    serializer_class = PersonalInfoSerializer
    related_name = 'personal_info'


class FamilyBackgroundView(SectionBaseView):
    model_class = FamilyBackground
    serializer_class = FamilyBackgroundSerializer
    related_name = 'family_background'


class EducationalBackgroundListView(ListSectionBaseView):
    model_class = EducationalBackground
    serializer_class = EducationalBackgroundSerializer
    related_name = 'educational_backgrounds'


class EducationalBackgroundDetailView(ListSectionDetailView):
    model_class = EducationalBackground
    serializer_class = EducationalBackgroundSerializer


class CivilServiceEligibilityListView(ListSectionBaseView):
    model_class = CivilServiceEligibility
    serializer_class = CivilServiceEligibilitySerializer
    related_name = 'civil_service_eligibilities'


class CivilServiceEligibilityDetailView(ListSectionDetailView):
    model_class = CivilServiceEligibility
    serializer_class = CivilServiceEligibilitySerializer


class WorkExperienceListView(ListSectionBaseView):
    model_class = WorkExperience
    serializer_class = WorkExperienceSerializer
    related_name = 'work_experiences'


class WorkExperienceDetailView(ListSectionDetailView):
    model_class = WorkExperience
    serializer_class = WorkExperienceSerializer


class LearningDevelopmentListView(ListSectionBaseView):
    model_class = LearningDevelopment
    serializer_class = LearningDevelopmentSerializer
    related_name = 'learning_developments'


class LearningDevelopmentDetailView(ListSectionDetailView):
    model_class = LearningDevelopment
    serializer_class = LearningDevelopmentSerializer


class VoluntaryWorkListView(ListSectionBaseView):
    model_class = VoluntaryWork
    serializer_class = VoluntaryWorkSerializer
    related_name = 'voluntary_works'


class VoluntaryWorkDetailView(ListSectionDetailView):
    model_class = VoluntaryWork
    serializer_class = VoluntaryWorkSerializer


class OtherInformationView(SectionBaseView):
    model_class = OtherInformation
    serializer_class = OtherInformationSerializer
    related_name = 'other_information'


class GovernmentQuestionsView(SectionBaseView):
    model_class = GovernmentQuestions
    serializer_class = GovernmentQuestionsSerializer
    related_name = 'government_questions'


class ReferenceListView(ListSectionBaseView):
    model_class = Reference
    serializer_class = ReferenceSerializer
    related_name = 'references'


class ReferenceDetailView(ListSectionDetailView):
    model_class = Reference
    serializer_class = ReferenceSerializer


class PDSDeclarationView(SectionBaseView):
    model_class = PDSDeclaration
    serializer_class = PDSDeclarationSerializer
    related_name = 'pds_declaration'
