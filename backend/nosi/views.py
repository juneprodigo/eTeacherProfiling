import json
from datetime import date
from django.http import HttpResponse, JsonResponse
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .models import (
    StepIncrementRecord,
    StepIncrementDocument,
    StepIncrementSalarySchedule,
    NosiAlert,
    ServiceRecordEntry,
    SalaryAdjustmentRecord,
    AppointmentRecord
)
from .serializers import (
    StepIncrementRecordSerializer,
    StepIncrementDocumentSerializer,
    StepIncrementSalaryScheduleSerializer,
    NosiAlertSerializer,
    ServiceRecordEntrySerializer,
    SalaryAdjustmentRecordSerializer,
    AppointmentRecordSerializer
)
from .services import calculate_teacher_step_eligibility, refresh_smart_alerts, lookup_salary
from .excel_export import (
    generate_deped_nosi_excel,
    generate_csc_service_record_excel,
    generate_deped_nosa_excel
)
from pds.models import Teacher


class StepIncrementRecordViewSet(viewsets.ModelViewSet):
    """
    CRUD for Step Increment Records (NOSI).
    Teachers can view their own records; HR/Admin can view all and manage.
    """
    serializer_class = StepIncrementRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        user = self.request.user
        qs = StepIncrementRecord.objects.select_related('teacher__user').prefetch_related('documents')
        if hasattr(user, 'role') and user.role in ['admin', 'hr']:
            teacher_id = self.request.query_params.get('teacher_id')
            if teacher_id:
                return qs.filter(teacher_id=teacher_id)
            return qs
        # Teacher view
        return qs.filter(teacher__user=user)

    def perform_create(self, serializer):
        # Auto-compute new salary / differential if not supplied
        data = serializer.validated_data
        sg = data.get('new_salary_grade', 11)
        step = data.get('new_step', 2)
        prev_salary = data.get('previous_monthly_salary')
        new_salary = data.get('new_monthly_salary')

        if not new_salary or new_salary == 0:
            new_salary = lookup_salary(sg, step)
            serializer.validated_data['new_monthly_salary'] = new_salary

        serializer.save()

    @action(detail=True, methods=['get'])
    def download_nosi_excel(self, request, pk=None):
        """Generates and downloads DepEd NOSI formatted official spreadsheet"""
        record = self.get_object()
        file_bytes = generate_deped_nosi_excel(record.id)
        filename = f"DepEd_NOSI_{record.nosi_number or record.id}.xlsx"

        response = HttpResponse(
            file_bytes,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    @action(detail=True, methods=['post'])
    def update_checklist(self, request, pk=None):
        """Update checklist for Key Requirements for Processing"""
        record = self.get_object()
        for field in [
            'has_approved_nosi', 'has_annex_d', 'has_payslips',
            'has_latest_appointment', 'has_updated_service_record'
        ]:
            if field in request.data:
                setattr(record, field, bool(request.data[field]))
        
        # Auto update status based on checklist
        all_reqs = [
            record.has_approved_nosi, record.has_annex_d, record.has_payslips,
            record.has_latest_appointment, record.has_updated_service_record
        ]
        if all(all_reqs):
            if record.status in ['ELIGIBLE_PENDING', 'DOCS_INCOMPLETE']:
                record.status = 'DOCS_VERIFIED'
        else:
            if record.status == 'DOCS_VERIFIED':
                record.status = 'DOCS_INCOMPLETE'

        record.save()
        return Response(StepIncrementRecordSerializer(record).data)


class StepIncrementDocumentViewSet(viewsets.ModelViewSet):
    """
    Upload and management of supporting documents for NOSI verification.
    """
    serializer_class = StepIncrementDocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        user = self.request.user
        qs = StepIncrementDocument.objects.select_related('record__teacher__user')
        if hasattr(user, 'role') and user.role in ['admin', 'hr']:
            return qs
        return qs.filter(record__teacher__user=user)

    def perform_create(self, serializer):
        doc = serializer.save()
        # Automatically mark the corresponding checklist boolean on the record
        record = doc.record
        doc_type = doc.doc_type
        if doc_type == 'APPROVED_NOSI':
            record.has_approved_nosi = True
        elif doc_type == 'ANNEX_D':
            record.has_annex_d = True
        elif doc_type == 'PAYSLIP':
            record.has_payslips = True
        elif doc_type == 'LATEST_APPOINTMENT':
            record.has_latest_appointment = True
        elif doc_type == 'SERVICE_RECORD':
            record.has_updated_service_record = True
        record.save()


class NosiAlertViewSet(viewsets.ModelViewSet):
    """
    Smart alerts & notification listing and dismiss/read handling.
    """
    serializer_class = NosiAlertSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = NosiAlert.objects.select_related('teacher__user')
        if hasattr(user, 'role') and user.role in ['admin', 'hr']:
            return qs
        return qs.filter(teacher__user=user)

    @action(detail=False, methods=['post'])
    def refresh(self, request):
        """Scans roster and generates smart alerts for upcoming/overdue step increments"""
        count = refresh_smart_alerts()
        return Response({'message': f'Smart alert engine finished. {count} new alerts generated.', 'new_alerts_count': count})

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        alert = self.get_object()
        alert.is_read = True
        alert.save()
        return Response({'status': 'marked as read'})

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        self.get_queryset().update(is_read=True)
        return Response({'status': 'all marked as read'})


class TeacherNosiEligibilityView(APIView):
    """
    Calculates step increment forecasting, next increment date, days remaining,
    and salary differential for any or all teachers.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        teacher_id = request.query_params.get('teacher_id')

        if hasattr(user, 'role') and user.role in ['admin', 'hr']:
            if teacher_id:
                teachers = Teacher.objects.filter(id=teacher_id)
            else:
                teachers = Teacher.objects.select_related('user').all()
        else:
            teachers = Teacher.objects.filter(user=user)

        today = date.today()
        results = []
        for t in teachers:
            results.append(calculate_teacher_step_eligibility(t, today))

        return Response(results)


class StepIncrementSalaryScheduleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = StepIncrementSalarySchedule.objects.all()
    serializer_class = StepIncrementSalaryScheduleSerializer
    permission_classes = [permissions.IsAuthenticated]


class ServiceRecordEntryViewSet(viewsets.ModelViewSet):
    """
    CRUD for CSC Form No. 122 — Teacher's Official Service Record.
    Supports file attachment uploads and official CSC Form 122 Excel generation.
    """
    serializer_class = ServiceRecordEntrySerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        user = self.request.user
        qs = ServiceRecordEntry.objects.select_related('teacher__user')
        if hasattr(user, 'role') and user.role in ['admin', 'hr']:
            teacher_id = self.request.query_params.get('teacher_id')
            if teacher_id:
                return qs.filter(teacher_id=teacher_id)
            return qs
        return qs.filter(teacher__user=user)

    def perform_create(self, serializer):
        user = self.request.user
        if hasattr(user, 'role') and user.role not in ['admin', 'hr']:
            teacher = getattr(user, 'teacher_profile', None)
            if not teacher:
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied("Teacher profile not found for this user account.")
            serializer.save(teacher=teacher)
        else:
            serializer.save()

    def perform_update(self, serializer):
        user = self.request.user
        if hasattr(user, 'role') and user.role not in ['admin', 'hr']:
            teacher = getattr(user, 'teacher_profile', None)
            serializer.save(teacher=teacher)
        else:
            serializer.save()

    @action(detail=False, methods=['get'])
    def download_csc_excel(self, request):
        """
        Download official CSC Form No. 122 Service Record Excel for a teacher.
        Query params: ?teacher_id=...
        """
        user = request.user
        teacher_id = request.query_params.get('teacher_id')

        if hasattr(user, 'role') and user.role in ['admin', 'hr']:
            if not teacher_id:
                return Response({'error': 'teacher_id parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
            teacher = Teacher.objects.filter(id=teacher_id).first()
        else:
            teacher = getattr(user, 'teacher_profile', None)

        if not teacher:
            return Response({'error': 'Teacher record not found'}, status=status.HTTP_404_NOT_FOUND)

        file_bytes = generate_csc_service_record_excel(teacher.id)
        teacher_name = teacher.user.get_full_name().replace(' ', '_') or f"Teacher_{teacher.id}"
        filename = f"CSC_Form_122_Service_Record_{teacher_name}.xlsx"

        response = HttpResponse(
            file_bytes,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response


class SalaryAdjustmentRecordViewSet(viewsets.ModelViewSet):
    """
    CRUD for Notice of Salary Adjustment (NOSA).
    Supports scanned document uploads and DepEd NOSA Excel generation.
    """
    serializer_class = SalaryAdjustmentRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        user = self.request.user
        qs = SalaryAdjustmentRecord.objects.select_related('teacher__user')
        if hasattr(user, 'role') and user.role in ['admin', 'hr']:
            teacher_id = self.request.query_params.get('teacher_id')
            if teacher_id:
                return qs.filter(teacher_id=teacher_id)
            return qs
        return qs.filter(teacher__user=user)

    @action(detail=True, methods=['get'])
    def download_nosa_excel(self, request, pk=None):
        """Download official DepEd NOSA spreadsheet"""
        nosa = self.get_object()
        file_bytes = generate_deped_nosa_excel(nosa.id)
        filename = f"DepEd_NOSA_{nosa.nosa_number or nosa.id}.xlsx"

        response = HttpResponse(
            file_bytes,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response


class AppointmentRecordViewSet(viewsets.ModelViewSet):
    """
    CRUD for CS Form No. 33 / KSS Pormularyo Blg. 33 — Teacher Plantilla Appointments.
    Supports scanned document attachments and historical tracking.
    """
    serializer_class = AppointmentRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        user = self.request.user
        qs = AppointmentRecord.objects.select_related('teacher__user')
        if hasattr(user, 'role') and user.role in ['admin', 'hr']:
            teacher_id = self.request.query_params.get('teacher_id')
            if teacher_id:
                return qs.filter(teacher_id=teacher_id)
            return qs
        return qs.filter(teacher__user=user)

