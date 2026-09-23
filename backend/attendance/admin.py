from django.contrib import admin
from .models import AttendanceShiftSetting, DailyTimeRecord, LeaveApplication, LeaveBalance


@admin.register(AttendanceShiftSetting)
class AttendanceShiftSettingAdmin(admin.ModelAdmin):
    list_display = ['name', 'am_start', 'am_end', 'pm_start', 'pm_end', 'grace_period_minutes', 'is_active']


@admin.register(DailyTimeRecord)
class DailyTimeRecordAdmin(admin.ModelAdmin):
    list_display = ['teacher', 'date', 'am_time_in', 'am_time_out', 'pm_time_in', 'pm_time_out', 'status', 'tardy_minutes', 'total_hours_rendered']
    list_filter = ['status', 'date']
    search_fields = ['teacher__user__first_name', 'teacher__user__last_name', 'teacher__employee_id']


@admin.register(LeaveApplication)
class LeaveApplicationAdmin(admin.ModelAdmin):
    list_display = ['teacher', 'leave_type', 'start_date', 'end_date', 'days_applied', 'status', 'reviewed_by']
    list_filter = ['status', 'leave_type']


@admin.register(LeaveBalance)
class LeaveBalanceAdmin(admin.ModelAdmin):
    list_display = ['teacher', 'vacation_leave', 'sick_leave', 'special_privilege_leave', 'updated_at']
