from django.contrib import admin
from .models import StepIncrementRecord, StepIncrementDocument, StepIncrementSalarySchedule, NosiAlert


class StepIncrementDocumentInline(admin.TabularInline):
    model = StepIncrementDocument
    extra = 1


@admin.register(StepIncrementRecord)
class StepIncrementRecordAdmin(admin.ModelAdmin):
    list_display = (
        'nosi_number', 'teacher', 'basis', 'status',
        'effective_date', 'previous_step', 'new_step',
        'monthly_differential', 'has_approved_nosi', 'has_annex_d',
        'has_payslips', 'has_latest_appointment', 'has_updated_service_record'
    )
    list_filter = ('status', 'basis', 'effective_date')
    search_fields = ('nosi_number', 'teacher__user__first_name', 'teacher__user__last_name', 'teacher__employee_id')
    inlines = [StepIncrementDocumentInline]


@admin.register(StepIncrementDocument)
class StepIncrementDocumentAdmin(admin.ModelAdmin):
    list_display = ('record', 'doc_type', 'title', 'is_verified', 'uploaded_at')
    list_filter = ('doc_type', 'is_verified')


@admin.register(NosiAlert)
class NosiAlertAdmin(admin.ModelAdmin):
    list_display = ('title', 'teacher', 'alert_type', 'severity', 'is_read', 'created_at')
    list_filter = ('alert_type', 'severity', 'is_read')
    search_fields = ('title', 'teacher__user__first_name', 'teacher__user__last_name')


@admin.register(StepIncrementSalarySchedule)
class StepIncrementSalaryScheduleAdmin(admin.ModelAdmin):
    list_display = ('tranche', 'salary_grade', 'step', 'monthly_salary')
    list_filter = ('tranche', 'salary_grade')
