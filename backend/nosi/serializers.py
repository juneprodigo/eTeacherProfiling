from rest_framework import serializers
from .models import (
    StepIncrementRecord,
    StepIncrementDocument,
    StepIncrementSalarySchedule,
    NosiAlert,
    ServiceRecordEntry,
    SalaryAdjustmentRecord,
    AppointmentRecord
)
from pds.models import Teacher


class StepIncrementSalaryScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = StepIncrementSalarySchedule
        fields = '__all__'


class StepIncrementDocumentSerializer(serializers.ModelSerializer):
    doc_type_display = serializers.CharField(source='get_doc_type_display', read_only=True)
    file_name = serializers.SerializerMethodField()

    class Meta:
        model = StepIncrementDocument
        fields = [
            'id', 'record', 'doc_type', 'doc_type_display', 'title',
            'file', 'file_name', 'is_verified', 'verification_notes', 'uploaded_at'
        ]

    def get_file_name(self, obj):
        return obj.file.name.split('/')[-1] if obj.file else ''


class StepIncrementRecordSerializer(serializers.ModelSerializer):
    teacher_name = serializers.SerializerMethodField()
    teacher_employee_id = serializers.CharField(source='teacher.employee_id', read_only=True)
    teacher_position = serializers.CharField(source='teacher.position', read_only=True)
    teacher_department = serializers.CharField(source='teacher.department', read_only=True)
    documents = StepIncrementDocumentSerializer(many=True, read_only=True)
    requirements_completion_rate = serializers.SerializerMethodField()
    file_name = serializers.SerializerMethodField()

    class Meta:
        model = StepIncrementRecord
        fields = [
            'id', 'teacher', 'teacher_name', 'teacher_employee_id', 'teacher_position', 'teacher_department',
            'basis', 'status', 'nosi_number', 'date_issued', 'effective_date',
            'previous_salary_grade', 'previous_step', 'previous_monthly_salary',
            'new_salary_grade', 'new_step', 'new_monthly_salary', 'monthly_differential',
            'schools_division_superintendent', 'division_office', 'school_name',
            'has_approved_nosi', 'has_annex_d', 'has_payslips',
            'has_latest_appointment', 'has_updated_service_record',
            'document_file', 'file_name',
            'documents', 'requirements_completion_rate', 'remarks',
            'created_at', 'updated_at'
        ]

    def get_teacher_name(self, obj):
        return obj.teacher.user.get_full_name() or obj.teacher.user.username

    def get_file_name(self, obj):
        return obj.document_file.name.split('/')[-1] if obj.document_file else ''

    def get_requirements_completion_rate(self, obj):
        checks = [
            obj.has_approved_nosi,
            obj.has_annex_d,
            obj.has_payslips,
            obj.has_latest_appointment,
            obj.has_updated_service_record,
        ]
        completed = sum(1 for c in checks if c)
        return {
            'completed': completed,
            'total': len(checks),
            'percentage': round((completed / len(checks)) * 100) if len(checks) else 0,
            'is_fully_compliant': completed == len(checks)
        }


class NosiAlertSerializer(serializers.ModelSerializer):
    teacher_name = serializers.SerializerMethodField()
    teacher_id = serializers.IntegerField(source='teacher.id', read_only=True)

    class Meta:
        model = NosiAlert
        fields = '__all__'

    def get_teacher_name(self, obj):
        return obj.teacher.user.get_full_name() or obj.teacher.user.username


class ServiceRecordEntrySerializer(serializers.ModelSerializer):
    teacher_name = serializers.SerializerMethodField()
    teacher_employee_id = serializers.CharField(source='teacher.employee_id', read_only=True)
    teacher_position = serializers.CharField(source='teacher.position', read_only=True)
    file_name = serializers.SerializerMethodField()

    class Meta:
        model = ServiceRecordEntry
        fields = [
            'id', 'teacher', 'teacher_name', 'teacher_employee_id', 'teacher_position',
            'from_date', 'to_date', 'to_present',
            'designation', 'status_of_appointment',
            'salary_grade', 'step', 'monthly_salary', 'annual_salary',
            'station_office', 'branch', 'lwop_dates',
            'separation_date', 'separation_cause', 'remarks',
            'document_file', 'file_name',
            'created_at', 'updated_at'
        ]

    def get_teacher_name(self, obj):
        return obj.teacher.user.get_full_name() or obj.teacher.user.username

    def get_file_name(self, obj):
        return obj.document_file.name.split('/')[-1] if obj.document_file else ''


class SalaryAdjustmentRecordSerializer(serializers.ModelSerializer):
    teacher_name = serializers.SerializerMethodField()
    teacher_employee_id = serializers.CharField(source='teacher.employee_id', read_only=True)
    teacher_position = serializers.CharField(source='teacher.position', read_only=True)
    file_name = serializers.SerializerMethodField()

    class Meta:
        model = SalaryAdjustmentRecord
        fields = [
            'id', 'teacher', 'teacher_name', 'teacher_employee_id', 'teacher_position',
            'nosa_number', 'date_issued', 'effective_date', 'legal_basis',
            'position_title', 'salary_grade', 'step',
            'previous_monthly_salary', 'adjusted_monthly_salary', 'monthly_differential',
            'status', 'signatory_authority', 'remarks',
            'document_file', 'file_name',
            'created_at', 'updated_at'
        ]

    def get_teacher_name(self, obj):
        return obj.teacher.user.get_full_name() or obj.teacher.user.username

    def get_file_name(self, obj):
        return obj.document_file.name.split('/')[-1] if obj.document_file else ''


class AppointmentRecordSerializer(serializers.ModelSerializer):
    teacher_name = serializers.SerializerMethodField()
    teacher_employee_id = serializers.CharField(source='teacher.employee_id', read_only=True)
    teacher_position = serializers.CharField(source='teacher.position', read_only=True)
    file_name = serializers.SerializerMethodField()

    class Meta:
        model = AppointmentRecord
        fields = [
            'id', 'teacher', 'teacher_name', 'teacher_employee_id', 'teacher_position',
            'appointment_number', 'position_title', 'plantilla_item_no',
            'nature_of_appointment', 'status_of_appointment',
            'salary_grade', 'step', 'monthly_rate', 'annual_rate',
            'date_of_signing', 'date_of_assumption', 'csc_attestation_date',
            'csc_action', 'vice_personnel', 'vice_reason', 'page_no_plantilla',
            'remarks', 'document_file', 'file_name',
            'created_at', 'updated_at'
        ]

    def get_teacher_name(self, obj):
        return obj.teacher.user.get_full_name() or obj.teacher.user.username

    def get_file_name(self, obj):
        return obj.document_file.name.split('/')[-1] if obj.document_file else ''

