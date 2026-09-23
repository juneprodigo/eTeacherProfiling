from rest_framework import serializers
from .models import AttendanceShiftSetting, DailyTimeRecord, LeaveApplication, LeaveBalance
from pds.models import Teacher


class AttendanceShiftSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceShiftSetting
        fields = '__all__'


class DailyTimeRecordSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.user.get_full_name', read_only=True)
    employee_id = serializers.CharField(source='teacher.employee_id', read_only=True)
    department = serializers.CharField(source='teacher.department', read_only=True)
    verified_by_name = serializers.CharField(source='verified_by.get_full_name', read_only=True, default='')

    class Meta:
        model = DailyTimeRecord
        fields = [
            'id', 'teacher', 'teacher_name', 'employee_id', 'department',
            'date', 'am_time_in', 'am_time_out', 'pm_time_in', 'pm_time_out',
            'status', 'tardy_minutes', 'undertime_minutes', 'total_hours_rendered',
            'remarks', 'is_manual_entry', 'verified_by', 'verified_by_name',
            'created_at', 'updated_at'
        ]


class LeaveBalanceSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.user.get_full_name', read_only=True)
    employee_id = serializers.CharField(source='teacher.employee_id', read_only=True)

    class Meta:
        model = LeaveBalance
        fields = [
            'id', 'teacher', 'teacher_name', 'employee_id',
            'vacation_leave', 'sick_leave', 'special_privilege_leave', 'updated_at'
        ]


class LeaveApplicationSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.user.get_full_name', read_only=True)
    employee_id = serializers.CharField(source='teacher.employee_id', read_only=True)
    department = serializers.CharField(source='teacher.department', read_only=True)
    reviewed_by_name = serializers.CharField(source='reviewed_by.get_full_name', read_only=True, default='')

    class Meta:
        model = LeaveApplication
        fields = [
            'id', 'teacher', 'teacher_name', 'employee_id', 'department',
            'leave_type', 'start_date', 'end_date', 'days_applied',
            'reason', 'status', 'reviewed_by', 'reviewed_by_name',
            'reviewed_at', 'admin_remarks', 'created_at', 'updated_at'
        ]
