import datetime
from django.db import models
from django.conf import settings
from pds.models import Teacher


class AttendanceShiftSetting(models.Model):
    """Configuration for official faculty work hours and grace period."""
    name = models.CharField(max_length=100, default='Standard Faculty Shift')
    am_start = models.TimeField(default=datetime.time(8, 0))
    am_end = models.TimeField(default=datetime.time(12, 0))
    pm_start = models.TimeField(default=datetime.time(13, 0))
    pm_end = models.TimeField(default=datetime.time(17, 0))
    grace_period_minutes = models.PositiveIntegerField(default=15, help_text='Grace period in minutes before marked Late')
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'attendance_shift_setting'
        verbose_name = 'Attendance Shift Setting'

    def __str__(self):
        return f'{self.name} ({self.am_start.strftime("%H:%M")} - {self.pm_end.strftime("%H:%M")})'


class DailyTimeRecord(models.Model):
    """
    Civil Service Form No. 48 — Daily Time Record (DTR)
    Tracks official arrival and departure for AM and PM shifts.
    """
    class Status(models.TextChoices):
        PRESENT = 'Present', 'Present'
        LATE = 'Late / Tardy', 'Late / Tardy'
        UNDERTIME = 'Undertime', 'Undertime'
        ABSENT = 'Absent', 'Absent'
        ON_LEAVE = 'On Leave', 'On Leave'
        OFFICIAL_BUSINESS = 'Official Business (OB)', 'Official Business (OB)'
        HOLIDAY = 'Holiday', 'Holiday'
        WEEKEND = 'Weekend', 'Weekend'
        SUSPENDED = 'Suspended', 'Suspended'

    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='daily_time_records')
    date = models.DateField(default=datetime.date.today)

    # 4 CSC Official Punches
    am_time_in = models.TimeField(null=True, blank=True, verbose_name='AM Arrival')
    am_time_out = models.TimeField(null=True, blank=True, verbose_name='AM Departure')
    pm_time_in = models.TimeField(null=True, blank=True, verbose_name='PM Arrival')
    pm_time_out = models.TimeField(null=True, blank=True, verbose_name='PM Departure')

    status = models.CharField(max_length=40, choices=Status.choices, default=Status.PRESENT)
    tardy_minutes = models.PositiveIntegerField(default=0, help_text='Minutes late beyond official schedule & grace period')
    undertime_minutes = models.PositiveIntegerField(default=0, help_text='Minutes of early departure')
    total_hours_rendered = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)

    remarks = models.CharField(max_length=255, blank=True, default='')
    is_manual_entry = models.BooleanField(default=False)
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='verified_dtrs'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'attendance_daily_record'
        ordering = ['-date', 'teacher']
        unique_together = ['teacher', 'date']
        verbose_name = 'Daily Time Record (CS Form 48)'

    def __str__(self):
        return f'{self.teacher} — {self.date.strftime("%Y-%m-%d")} ({self.status})'

    def recalculate(self, shift=None):
        """Calculates tardiness, undertime, and total hours based on official shifts."""
        if not shift:
            shift = AttendanceShiftSetting.objects.filter(is_active=True).first()
            if not shift:
                shift = AttendanceShiftSetting()

        tardy = 0
        undertime = 0
        total_seconds = 0

        # AM Calculation
        if self.am_time_in:
            am_start_dt = datetime.datetime.combine(self.date, shift.am_start)
            am_in_dt = datetime.datetime.combine(self.date, self.am_time_in)
            late_delta = (am_in_dt - am_start_dt).total_seconds() / 60
            if late_delta > shift.grace_period_minutes:
                tardy += int(late_delta)

            if self.am_time_out:
                am_out_dt = datetime.datetime.combine(self.date, self.am_time_out)
                am_end_dt = datetime.datetime.combine(self.date, shift.am_end)
                if am_out_dt < am_end_dt:
                    undertime += int((am_end_dt - am_out_dt).total_seconds() / 60)
                if am_out_dt > am_in_dt:
                    total_seconds += (am_out_dt - am_in_dt).total_seconds()

        # PM Calculation
        if self.pm_time_in:
            pm_start_dt = datetime.datetime.combine(self.date, shift.pm_start)
            pm_in_dt = datetime.datetime.combine(self.date, self.pm_time_in)
            late_delta = (pm_in_dt - pm_start_dt).total_seconds() / 60
            if late_delta > shift.grace_period_minutes:
                tardy += int(late_delta)

            if self.pm_time_out:
                pm_out_dt = datetime.datetime.combine(self.date, self.pm_time_out)
                pm_end_dt = datetime.datetime.combine(self.date, shift.pm_end)
                if pm_out_dt < pm_end_dt:
                    undertime += int((pm_end_dt - pm_out_dt).total_seconds() / 60)
                if pm_out_dt > pm_in_dt:
                    total_seconds += (pm_out_dt - pm_in_dt).total_seconds()

        self.tardy_minutes = tardy
        self.undertime_minutes = undertime
        self.total_hours_rendered = round(total_seconds / 3600.0, 2)

        if self.status not in [self.Status.ON_LEAVE, self.Status.OFFICIAL_BUSINESS, self.Status.HOLIDAY, self.Status.SUSPENDED]:
            if not self.am_time_in and not self.pm_time_in:
                self.status = self.Status.ABSENT
            elif tardy > 0:
                self.status = self.Status.LATE
            elif undertime > 0:
                self.status = self.Status.UNDERTIME
            else:
                self.status = self.Status.PRESENT


class LeaveApplication(models.Model):
    """
    Civil Service Form No. 6 — Application for Leave
    """
    class LeaveType(models.TextChoices):
        VACATION = 'Vacation Leave', 'Vacation Leave (Sec. 51, Rule XVI)'
        MANDATORY = 'Mandatory / Forced Leave', 'Mandatory / Forced Leave (Sec. 25, Rule XVI)'
        SICK = 'Sick Leave', 'Sick Leave (Sec. 43, Rule XVI)'
        MATERNITY = 'Maternity Leave', 'Maternity Leave (RA 11210 / CSC MC 05, s. 2021)'
        PATERNITY = 'Paternity Leave', 'Paternity Leave (RA 8187 / CSC MC 71, s. 1998)'
        SPL = 'Special Privilege Leave (SPL)', 'Special Privilege Leave (Rule XVI, Sec. 21)'
        SOLO_PARENT = 'Solo Parent Leave', 'Solo Parent Leave (RA 8972 / RA 11861)'
        STUDY = 'Study Leave', 'Study Leave (Sec. 68, Rule XVI)'
        VAWC = '10-Day VAWC Leave', '10-Day VAWC Leave (RA 9262)'
        REHAB = 'Rehabilitation Privilege', 'Rehabilitation Privilege (Sec. 55, Rule XVI)'
        OTHERS = 'Others', 'Others'

    class Status(models.TextChoices):
        PENDING = 'Pending', 'Pending HR Review'
        APPROVED = 'Approved', 'Approved'
        DISAPPROVED = 'Disapproved', 'Disapproved'
        CANCELLED = 'Cancelled', 'Cancelled'

    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='leave_applications')
    leave_type = models.CharField(max_length=60, choices=LeaveType.choices, default=LeaveType.VACATION)
    start_date = models.DateField()
    end_date = models.DateField()
    days_applied = models.DecimalField(max_digits=4, decimal_places=1, default=1.0)
    reason = models.TextField(help_text='Details / justification for leave application')

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='reviewed_leaves'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    admin_remarks = models.TextField(blank=True, default='')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'attendance_leave_application'
        ordering = ['-created_at']
        verbose_name = 'Application for Leave (CS Form 6)'

    def __str__(self):
        return f'{self.teacher} — {self.leave_type} ({self.start_date} to {self.end_date}) [{self.status}]'


class LeaveBalance(models.Model):
    """Maintains official leave credit balance for a faculty member."""
    teacher = models.OneToOneField(Teacher, on_delete=models.CASCADE, related_name='leave_balance')
    vacation_leave = models.DecimalField(max_digits=5, decimal_places=2, default=15.0)
    sick_leave = models.DecimalField(max_digits=5, decimal_places=2, default=15.0)
    special_privilege_leave = models.DecimalField(max_digits=5, decimal_places=2, default=3.0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'attendance_leave_balance'
        verbose_name = 'Leave Credit Balance'

    def __str__(self):
        return f'Credits: {self.teacher} (VL: {self.vacation_leave}, SL: {self.sick_leave}, SPL: {self.special_privilege_leave})'
