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
    TrainingLibrary, VoluntaryWorkLibrary, WorkExperienceLibrary, EligibilityLibrary,
)
from .serializers import (
    TeacherListSerializer, TeacherCreateSerializer, TeacherUpdateSerializer,
    PersonalInfoSerializer, FamilyBackgroundSerializer,
    EducationalBackgroundSerializer, CivilServiceEligibilitySerializer,
    WorkExperienceSerializer, LearningDevelopmentSerializer,
    VoluntaryWorkSerializer, OtherInformationSerializer,
    GovernmentQuestionsSerializer, ReferenceSerializer,
    PDSDeclarationSerializer, PDSSummarySerializer,
    TrainingLibrarySerializer, VoluntaryWorkLibrarySerializer,
    WorkExperienceLibrarySerializer, EligibilityLibrarySerializer,
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


_WEASYPRINT_AVAILABLE = None

def _is_weasyprint_available():
    global _WEASYPRINT_AVAILABLE
    if _WEASYPRINT_AVAILABLE is None:
        try:
            import weasyprint  # noqa: F401
            _WEASYPRINT_AVAILABLE = True
        except Exception:
            _WEASYPRINT_AVAILABLE = False
    return _WEASYPRINT_AVAILABLE


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

        # 1. Children Partitioning (Sheet C1 capacity: 12 rows; overflow to Sheet C7)
        fb = getattr(teacher, 'family_background', None)
        all_children = list(fb.children.all()) if fb else []
        c1_children = all_children[:12]
        c7_children_overflow = all_children[12:]
        c1_children_padded = c1_children + [None] * (12 - len(c1_children))

        # 2. Educational Background (Sheet C1 standard: 1 per level; overflow to Sheet C8)
        all_edus = list(teacher.educational_backgrounds.all())
        level_map = {
            'Elementary': None,
            'Secondary': None,
            'Vocational/Trade Course': None,
            'College': None,
            'Graduate Studies': None,
        }
        c8_edus_overflow = []
        for edu in all_edus:
            lvl = edu.level
            if lvl in level_map and level_map[lvl] is None:
                level_map[lvl] = edu
            else:
                c8_edus_overflow.append(edu)

        # 3. Civil Service Eligibility (Sheet C2 capacity: 7 rows; overflow to Sheet C9)
        all_cses = list(teacher.civil_service_eligibilities.all())
        c2_cses = all_cses[:7]
        c9_cses_overflow = all_cses[7:]
        c2_cses_padded = c2_cses + [None] * (7 - len(c2_cses))

        # 4. Work Experience (Sheet C2 capacity: 26 rows; overflow to Sheet C6)
        all_wes = list(teacher.work_experiences.all())
        c2_wes = all_wes[:26]
        c6_wes_overflow = all_wes[26:]
        c2_wes_padded = c2_wes + [None] * (26 - len(c2_wes))

        # 5. Learning & Development (Sheet C3 capacity: 19 rows; overflow to Sheet C5)
        all_lds = list(teacher.learning_developments.all())
        c3_lds = all_lds[:19]
        c5_lds_overflow = all_lds[19:]
        c3_lds_padded = c3_lds + [None] * (19 - len(c3_lds))

        # 6. Voluntary Work (Sheet C3 capacity: 11 rows; overflow to Sheet C10)
        all_vws = list(teacher.voluntary_works.all())
        c3_vws = all_vws[:11]
        c10_vws_overflow = all_vws[11:]
        c3_vws_padded = c3_vws + [None] * (11 - len(c3_vws))

        # 7. Other Information (Sheet C3 capacity: 7 rows; overflow to Sheet C11)
        other_info = getattr(teacher, 'other_information', None)
        skills = other_info.special_skills_hobbies if other_info else []
        distinctions = other_info.non_academic_distinctions if other_info else []
        memberships = other_info.organization_memberships if other_info else []
        max_other_len = max(len(skills), len(distinctions), len(memberships), 7)
        c3_other_rows = []
        c11_other_overflow = []
        for i in range(max_other_len):
            row = {
                'skill': skills[i] if i < len(skills) else '',
                'distinction': distinctions[i] if i < len(distinctions) else '',
                'membership': memberships[i] if i < len(memberships) else ''
            }
            if i < 7:
                c3_other_rows.append(row)
            else:
                if row['skill'] or row['distinction'] or row['membership']:
                    c11_other_overflow.append(row)

        # 8. References (Sheet C4 capacity: 3 rows)
        all_refs = list(teacher.references.all())
        c4_refs_padded = all_refs[:3] + [None] * (3 - len(all_refs[:3]))

        # Flags for extra continuation sheets ("PRINT ONLY THE EXTRA SHEET/S WHERE ADDITIONAL INFORMATION WERE ENTERED THEREIN")
        has_c7 = len(c7_children_overflow) > 0
        has_c8 = len(c8_edus_overflow) > 0
        has_c9 = len(c9_cses_overflow) > 0
        has_c6 = len(c6_wes_overflow) > 0
        has_c5 = len(c5_lds_overflow) > 0
        has_c10 = len(c10_vws_overflow) > 0
        has_c11 = len(c11_other_overflow) > 0
        extra_count = sum([has_c5, has_c6, has_c7, has_c8, has_c9, has_c10, has_c11])
        total_pds_pages = 4 + extra_count

        photo_data_uri = None
        photo_field = teacher.photo if teacher.photo else (teacher.user.profile_photo if teacher.user.profile_photo else None)
        if photo_field:
            try:
                import base64
                with open(photo_field.path, 'rb') as pf:
                    ext = photo_field.name.split('.')[-1].lower()
                    mime = 'image/jpeg' if ext in ('jpg', 'jpeg') else ('image/png' if ext == 'png' else 'image/jpeg')
                    b64 = base64.b64encode(pf.read()).decode('utf-8')
                    photo_data_uri = f'data:{mime};base64,{b64}'
            except Exception:
                pass

        signature_data_uri = None
        if teacher.signature_image:
            try:
                import base64
                with open(teacher.signature_image.path, 'rb') as sf:
                    ext = teacher.signature_image.name.split('.')[-1].lower()
                    mime = 'image/png' if ext == 'png' else 'image/jpeg'
                    b64 = base64.b64encode(sf.read()).decode('utf-8')
                    signature_data_uri = f'data:{mime};base64,{b64}'
            except Exception:
                pass

        context = {
            'teacher': teacher,
            'personal_info': getattr(teacher, 'personal_info', None),
            'family_background': fb,
            'c1_children_padded': c1_children_padded,
            'c7_children_overflow': c7_children_overflow,
            'has_c7': has_c7,
            'level_map': level_map,
            'c8_edus_overflow': c8_edus_overflow,
            'has_c8': has_c8,
            'c2_cses_padded': c2_cses_padded,
            'c9_cses_overflow': c9_cses_overflow,
            'has_c9': has_c9,
            'c2_wes_padded': c2_wes_padded,
            'c6_wes_overflow': c6_wes_overflow,
            'has_c6': has_c6,
            'c3_lds_padded': c3_lds_padded,
            'c5_lds_overflow': c5_lds_overflow,
            'has_c5': has_c5,
            'c3_vws_padded': c3_vws_padded,
            'c10_vws_overflow': c10_vws_overflow,
            'has_c10': has_c10,
            'c3_other_rows': c3_other_rows,
            'c11_other_overflow': c11_other_overflow,
            'has_c11': has_c11,
            'government_questions': getattr(teacher, 'government_questions', None),
            'c4_refs_padded': c4_refs_padded,
            'pds_declaration': getattr(teacher, 'pds_declaration', None),
            'total_pds_pages': total_pds_pages,
            'photo_data_uri': photo_data_uri,
            'signature_data_uri': signature_data_uri,
        }

        # 1. Attempt verbatim Excel-based PDF generation (pixel-perfect to CS Form 212 Revised 2026)
        try:
            from .excel_exporter import PDSExcelExporter
            from .excel_to_pdf import convert_workbook_to_pdf
            exporter = PDSExcelExporter(teacher)
            wb = exporter.generate()
            verbatim_pdf = convert_workbook_to_pdf(wb, timeout_sec=20)
            if verbatim_pdf:
                name = teacher.user.get_full_name().replace(',', '').replace(' ', '_').strip()
                if not name:
                    name = teacher.employee_id or f'teacher_{teacher.pk}'
                response = HttpResponse(verbatim_pdf, content_type='application/pdf')
                response['Content-Disposition'] = f'inline; filename="PDS_{name}.pdf"'
                response['Access-Control-Expose-Headers'] = 'Content-Disposition'
                return response
        except Exception as ex:
            print("Verbatim Excel PDF export skipped, falling back to HTML renderer:", ex)

        # 2. Resilient fallback: HTML template renderer (xhtml2pdf / WeasyPrint)
        html_string = render_to_string('pds/pds_export.html', context)
        try:
            pdf_data = None
            if _is_weasyprint_available():
                try:
                    import weasyprint
                    pdf_data = weasyprint.HTML(string=html_string, base_url=request.build_absolute_uri('/')).write_pdf()
                except Exception:
                    pass

            if pdf_data is None:
                from xhtml2pdf import pisa
                import io
                pdf_buffer = io.BytesIO()
                pisa_status = pisa.CreatePDF(html_string, dest=pdf_buffer)
                if pisa_status.err:
                    return Response({'error': 'PDF rendering error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                pdf_data = pdf_buffer.getvalue()

            response = HttpResponse(pdf_data, content_type='application/pdf')
            name = teacher.user.get_full_name().replace(',', '').replace(' ', '_').strip()
            if not name:
                name = teacher.employee_id or f'teacher_{teacher.pk}'
            response['Content-Disposition'] = f'inline; filename="PDS_{name}.pdf"'
            response['Access-Control-Expose-Headers'] = 'Content-Disposition'
            return response
        except Exception as e:
            return Response({'error': f'PDF generation failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['get'], url_path='export-excel')
    def export_excel(self, request, pk=None):
        """Generates and downloads the official CS Form 212 Revised 2026 Excel spreadsheet with all teacher data."""
        teacher = self.get_object()
        from .excel_exporter import PDSExcelExporter
        try:
            exporter = PDSExcelExporter(teacher)
            stream = exporter.save_to_stream()
            last_name = (teacher.user.last_name if teacher.user else 'Teacher') or 'Teacher'
            first_name = (teacher.user.first_name if teacher.user else '') or ''
            filename = f"CS_Form_212_Revised_2026_{last_name}_{first_name}.xlsx".replace(" ", "_")

            response = HttpResponse(
                stream.getvalue(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            response['Access-Control-Expose-Headers'] = 'Content-Disposition'
            return response
        except Exception as e:
            return Response({'error': f'Excel export failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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


# ── Reference Libraries ViewSets ─────────────────────────────────────────────

class TrainingLibraryViewSet(viewsets.ModelViewSet):
    queryset = TrainingLibrary.objects.filter(is_active=True)
    serializer_class = TrainingLibrarySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None
    filterset_fields = ['ld_type', 'is_active']
    search_fields = ['training_title', 'conducted_sponsored_by']


class VoluntaryWorkLibraryViewSet(viewsets.ModelViewSet):
    queryset = VoluntaryWorkLibrary.objects.filter(is_active=True)
    serializer_class = VoluntaryWorkLibrarySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None
    search_fields = ['organization_name_address', 'position_nature_of_work']


class WorkExperienceLibraryViewSet(viewsets.ModelViewSet):
    queryset = WorkExperienceLibrary.objects.filter(is_active=True)
    serializer_class = WorkExperienceLibrarySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None
    search_fields = ['position_title', 'department_agency_company']


class EligibilityLibraryViewSet(viewsets.ModelViewSet):
    queryset = EligibilityLibrary.objects.filter(is_active=True)
    serializer_class = EligibilityLibrarySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None
    search_fields = ['eligibility_type']

