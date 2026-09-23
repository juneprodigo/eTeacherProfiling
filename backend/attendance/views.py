import calendar
import datetime
from django.utils import timezone
from django.db.models import Count, Q, Sum
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import HttpResponse

from .models import AttendanceShiftSetting, DailyTimeRecord, LeaveApplication, LeaveBalance
from .serializers import (
    AttendanceShiftSettingSerializer,
    DailyTimeRecordSerializer,
    LeaveApplicationSerializer,
    LeaveBalanceSerializer
)
from pds.models import Teacher


class DailyTimeRecordViewSet(viewsets.ModelViewSet):
    queryset = DailyTimeRecord.objects.select_related('teacher__user', 'verified_by').all()
    serializer_class = DailyTimeRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        # If user is a teacher and not HR/Admin, only show own records
        if not (user.is_staff or getattr(user, 'role', '') in ['admin', 'hr']):
            qs = qs.filter(teacher__user=user)

        # Filters
        teacher_id = self.request.query_params.get('teacher')
        if teacher_id:
            qs = qs.filter(teacher_id=teacher_id)

        date_str = self.request.query_params.get('date')
        if date_str:
            qs = qs.filter(date=date_str)

        month = self.request.query_params.get('month')
        year = self.request.query_params.get('year')
        if month and year:
            qs = qs.filter(date__year=year, date__month=month)

        status_param = self.request.query_params.get('status')
        if status_param and status_param != 'All':
            qs = qs.filter(status=status_param)

        return qs

    @action(detail=False, methods=['get'])
    def faculty_list(self, request):
        """
        Returns all registered users/faculty for Time & Attendance selector,
        ensuring every registered user has an active teacher/employee profile.
        """
        from django.contrib.auth import get_user_model
        User = get_user_model()
        users = User.objects.filter(is_active=True).order_by('last_name', 'first_name')

        results = []
        for u in users:
            teacher = getattr(u, 'teacher_profile', None)
            if not teacher:
                dept = 'Administration' if u.role == 'admin' else ('Human Resources' if u.role == 'hr' else 'Faculty Department')
                pos = 'School Administrator' if u.role == 'admin' else ('HR Officer' if u.role == 'hr' else 'Faculty Teacher')
                emp_id = f'DEPED-{u.role.upper()[:3]}-{u.id:04d}'
                teacher, _ = Teacher.objects.get_or_create(
                    user=u,
                    defaults={'employee_id': emp_id, 'department': dept, 'position': pos}
                )
                LeaveBalance.objects.get_or_create(teacher=teacher)

            results.append({
                'id': teacher.id,
                'user_id': u.id,
                'username': u.username,
                'full_name': u.get_full_name() or u.username,
                'employee_id': teacher.employee_id or f'EMP-{u.id:04d}',
                'department': teacher.department or u.get_role_display(),
                'position': teacher.position or u.get_role_display(),
                'role': u.role,
                'role_display': u.get_role_display(),
                'email': u.email
            })

        return Response(results)

    @action(detail=False, methods=['get'])
    def today_status(self, request):
        """Returns today's punch status and shift configuration for the current teacher."""
        user = request.user
        teacher = getattr(user, 'teacher_profile', None)

        teacher_id = request.query_params.get('teacher')
        if teacher_id:
            teacher = Teacher.objects.filter(id=teacher_id).first()

        if not teacher:
            teacher = Teacher.objects.first()

        if not teacher:
            return Response({'error': 'No teacher profile available.'}, status=status.HTTP_404_NOT_FOUND)

        today = datetime.date.today()
        record = DailyTimeRecord.objects.filter(teacher=teacher, date=today).first()
        shift = AttendanceShiftSetting.objects.filter(is_active=True).first()
        if not shift:
            shift = AttendanceShiftSetting()

        return Response({
            'today': today.isoformat(),
            'server_time': timezone.localtime(timezone.now()).strftime('%H:%M:%S'),
            'teacher': {
                'id': teacher.id,
                'name': teacher.user.get_full_name(),
                'employee_id': teacher.employee_id,
                'department': teacher.department,
            },
            'record': DailyTimeRecordSerializer(record).data if record else None,
            'shift': {
                'am_start': shift.am_start.strftime('%H:%M'),
                'am_end': shift.am_end.strftime('%H:%M'),
                'pm_start': shift.pm_start.strftime('%H:%M'),
                'pm_end': shift.pm_end.strftime('%H:%M'),
                'grace_period_minutes': shift.grace_period_minutes,
            }
        })

    @action(detail=False, methods=['post'])
    def clock_punch(self, request):
        """
        One-click digital time punch for faculty members:
        punch_type in ['am_in', 'am_out', 'pm_in', 'pm_out']
        """
        user = request.user
        teacher = getattr(user, 'teacher_profile', None)

        target_teacher_id = request.data.get('teacher_id')
        if target_teacher_id:
            teacher = Teacher.objects.filter(id=target_teacher_id).first()

        if not teacher:
            teacher = Teacher.objects.first()

        if not teacher:
            return Response({'error': 'No teacher profile found.'}, status=status.HTTP_404_NOT_FOUND)

        punch_type = request.data.get('punch_type')
        if punch_type not in ['am_in', 'am_out', 'pm_in', 'pm_out']:
            return Response({'error': f'Invalid punch_type: {punch_type}'}, status=status.HTTP_400_BAD_REQUEST)

        now = timezone.localtime(timezone.now())
        current_date = now.date()
        current_time = now.time().replace(microsecond=0)

        record, _ = DailyTimeRecord.objects.get_or_create(
            teacher=teacher,
            date=current_date,
            defaults={'status': DailyTimeRecord.Status.PRESENT}
        )

        if punch_type == 'am_in':
            record.am_time_in = current_time
        elif punch_type == 'am_out':
            record.am_time_out = current_time
        elif punch_type == 'pm_in':
            record.pm_time_in = current_time
        elif punch_type == 'pm_out':
            record.pm_time_out = current_time

        shift = AttendanceShiftSetting.objects.filter(is_active=True).first()
        record.recalculate(shift)
        record.save()

        return Response({
            'message': f'Successfully punched {punch_type.upper().replace("_", " ")} at {current_time.strftime("%I:%M %p")}',
            'record': DailyTimeRecordSerializer(record).data
        })

    @action(detail=False, methods=['get'])
    def monthly_dtr(self, request):
        """
        Returns official Civil Service Form No. 48 matrix for all days (1 to 31)
        in the requested month, with tardiness and undertime aggregates.
        """
        user = request.user
        teacher_id = request.query_params.get('teacher')
        if not teacher_id:
            teacher = getattr(user, 'teacher_profile', None)
            if teacher:
                teacher_id = teacher.id
            else:
                first_t = Teacher.objects.first()
                teacher_id = first_t.id if first_t else None

        if not teacher_id:
            return Response({'error': 'Teacher not specified.'}, status=status.HTTP_404_NOT_FOUND)

        teacher = Teacher.objects.filter(id=teacher_id).select_related('user').first()
        if not teacher:
            return Response({'error': 'Teacher not found.'}, status=status.HTTP_404_NOT_FOUND)

        now = datetime.date.today()
        month = int(request.query_params.get('month', now.month))
        year = int(request.query_params.get('year', now.year))

        _, num_days = calendar.monthrange(year, month)
        existing_records = {
            r.date.day: r for r in DailyTimeRecord.objects.filter(
                teacher=teacher, date__year=year, date__month=month
            )
        }

        days_matrix = []
        total_tardy_mins = 0
        total_undertime_mins = 0
        total_rendered_hours = 0.0
        days_present = 0
        days_absent = 0
        days_leave = 0

        for day in range(1, num_days + 1):
            cur_date = datetime.date(year, month, day)
            is_weekend = cur_date.weekday() >= 5
            rec = existing_records.get(day)

            if rec:
                am_in = rec.am_time_in.strftime('%H:%M') if rec.am_time_in else ''
                am_out = rec.am_time_out.strftime('%H:%M') if rec.am_time_out else ''
                pm_in = rec.pm_time_in.strftime('%H:%M') if rec.pm_time_in else ''
                pm_out = rec.pm_time_out.strftime('%H:%M') if rec.pm_time_out else ''
                status_val = rec.status
                tardy = rec.tardy_minutes
                undertime = rec.undertime_minutes
                hours = float(rec.total_hours_rendered)
                remarks = rec.remarks
            else:
                am_in = am_out = pm_in = pm_out = ''
                status_val = 'Weekend' if is_weekend else ('Absent' if cur_date < now else '')
                tardy = 0
                undertime = 0
                hours = 0.0
                remarks = ''

            # Tally metrics
            if status_val in ['Present', 'Late / Tardy', 'Undertime']:
                days_present += 1
            elif status_val == 'Absent':
                days_absent += 1
            elif status_val == 'On Leave':
                days_leave += 1

            total_tardy_mins += tardy
            total_undertime_mins += undertime
            total_rendered_hours += hours

            days_matrix.append({
                'day': day,
                'date': cur_date.isoformat(),
                'day_name': cur_date.strftime('%a'),
                'is_weekend': is_weekend,
                'am_time_in': am_in,
                'am_time_out': am_out,
                'pm_time_in': pm_in,
                'pm_time_out': pm_out,
                'tardy_minutes': tardy,
                'undertime_minutes': undertime,
                'total_hours': hours,
                'status': status_val,
                'remarks': remarks
            })

        tardy_hours = total_tardy_mins // 60
        tardy_rem_mins = total_tardy_mins % 60
        undertime_hours = total_undertime_mins // 60
        undertime_rem_mins = total_undertime_mins % 60

        return Response({
            'teacher': {
                'id': teacher.id,
                'name': teacher.user.get_full_name(),
                'employee_id': teacher.employee_id,
                'department': teacher.department,
                'position': teacher.position,
            },
            'month': month,
            'year': year,
            'month_name': calendar.month_name[month],
            'days': days_matrix,
            'summary': {
                'days_present': days_present,
                'days_absent': days_absent,
                'days_leave': days_leave,
                'total_tardy_minutes': total_tardy_mins,
                'tardy_formatted': f'{tardy_hours}h {tardy_rem_mins}m' if total_tardy_mins > 0 else '0m',
                'total_undertime_minutes': total_undertime_mins,
                'undertime_formatted': f'{undertime_hours}h {undertime_rem_mins}m' if total_undertime_mins > 0 else '0m',
                'total_hours_rendered': round(total_rendered_hours, 2),
            }
        })

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Campus-wide real-time attendance KPIs."""
        today = datetime.date.today()
        total_teachers = Teacher.objects.count()

        records_today = DailyTimeRecord.objects.filter(date=today)
        present_count = records_today.filter(
            status__in=[DailyTimeRecord.Status.PRESENT, DailyTimeRecord.Status.LATE, DailyTimeRecord.Status.UNDERTIME]
        ).count()
        tardy_count = records_today.filter(status=DailyTimeRecord.Status.LATE).count()
        on_leave_count = records_today.filter(status=DailyTimeRecord.Status.ON_LEAVE).count()
        absent_count = records_today.filter(status=DailyTimeRecord.Status.ABSENT).count()

        pending_leaves = LeaveApplication.objects.filter(status=LeaveApplication.Status.PENDING).count()
        attendance_rate = round((present_count / total_teachers * 100), 1) if total_teachers > 0 else 0

        total_tardy_today = records_today.aggregate(Sum('tardy_minutes'))['tardy_minutes__sum'] or 0

        return Response({
            'total_teachers': total_teachers,
            'today_present': present_count,
            'today_tardy': tardy_count,
            'today_on_leave': on_leave_count,
            'today_absent': absent_count,
            'today_attendance_rate': attendance_rate,
            'total_tardy_minutes_today': total_tardy_today,
            'pending_leaves_count': pending_leaves,
        })


class LeaveApplicationViewSet(viewsets.ModelViewSet):
    queryset = LeaveApplication.objects.select_related('teacher__user', 'reviewed_by').all()
    serializer_class = LeaveApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if not (user.is_staff or getattr(user, 'role', '') in ['admin', 'hr']):
            qs = qs.filter(teacher__user=user)

        status_param = self.request.query_params.get('status')
        if status_param and status_param != 'All':
            qs = qs.filter(status=status_param)

        return qs

    def perform_create(self, serializer):
        user = self.request.user
        teacher = getattr(user, 'teacher_profile', None)
        if not teacher:
            # Allow admin to specify teacher in body
            teacher_id = self.request.data.get('teacher')
            if teacher_id:
                teacher = Teacher.objects.filter(id=teacher_id).first()
        serializer.save(teacher=teacher)

    @action(detail=True, methods=['post'])
    def review(self, request, pk=None):
        """Approve or Disapprove a leave application and update leave credits."""
        leave = self.get_object()
        new_status = request.data.get('status')
        remarks = request.data.get('remarks', '')

        if new_status not in [LeaveApplication.Status.APPROVED, LeaveApplication.Status.DISAPPROVED, LeaveApplication.Status.CANCELLED]:
            return Response({'error': f'Invalid status: {new_status}'}, status=status.HTTP_400_BAD_REQUEST)

        leave.status = new_status
        leave.admin_remarks = remarks
        leave.reviewed_by = request.user
        leave.reviewed_at = timezone.now()
        leave.save()

        # If approved, deduct leave balance
        if new_status == LeaveApplication.Status.APPROVED:
            balance, _ = LeaveBalance.objects.get_or_create(teacher=leave.teacher)
            days = float(leave.days_applied)

            if 'Sick' in leave.leave_type:
                balance.sick_leave = max(0, float(balance.sick_leave) - days)
            elif 'Special' in leave.leave_type:
                balance.special_privilege_leave = max(0, float(balance.special_privilege_leave) - days)
            else:
                balance.vacation_leave = max(0, float(balance.vacation_leave) - days)
            balance.save()

            # Mark affected DTR dates as On Leave
            cur = leave.start_date
            while cur <= leave.end_date:
                if cur.weekday() < 5:  # Weekdays only
                    rec, _ = DailyTimeRecord.objects.get_or_create(
                        teacher=leave.teacher,
                        date=cur,
                        defaults={'status': DailyTimeRecord.Status.ON_LEAVE, 'remarks': f'Leave: {leave.leave_type}'}
                    )
                    rec.status = DailyTimeRecord.Status.ON_LEAVE
                    rec.remarks = f'Leave: {leave.leave_type}'
                    rec.save()
                cur += datetime.timedelta(days=1)

        return Response({
            'message': f'Leave application {new_status.lower()} successfully.',
            'leave': LeaveApplicationSerializer(leave).data
        })


class LeaveBalanceViewSet(viewsets.ModelViewSet):
    queryset = LeaveBalance.objects.select_related('teacher__user').all()
    serializer_class = LeaveBalanceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if not (user.is_staff or getattr(user, 'role', '') in ['admin', 'hr']):
            qs = qs.filter(teacher__user=user)
        return qs
