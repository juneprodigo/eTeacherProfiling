import os
import django
import datetime
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from pds.models import Teacher
from attendance.models import AttendanceShiftSetting, DailyTimeRecord, LeaveApplication, LeaveBalance
from django.contrib.auth import get_user_model

User = get_user_model()
admin_user = User.objects.filter(is_superuser=True).first() or User.objects.first()

# 1. Shift Setting
shift, _ = AttendanceShiftSetting.objects.get_or_create(
    name='Standard Faculty Shift',
    defaults={
        'am_start': datetime.time(8, 0),
        'am_end': datetime.time(12, 0),
        'pm_start': datetime.time(13, 0),
        'pm_end': datetime.time(17, 0),
        'grace_period_minutes': 15,
        'is_active': True,
    }
)
print("Shift setting verified:", shift)

# 2. Leave Balances and DTRs for Teachers
teachers = Teacher.objects.all()
today = datetime.date.today()
year = today.year
month = today.month

for teacher in teachers:
    # Ensure Leave Balance
    lb, _ = LeaveBalance.objects.get_or_create(
        teacher=teacher,
        defaults={
            'vacation_leave': 15.0,
            'sick_leave': 15.0,
            'special_privilege_leave': 3.0,
        }
    )

    # Seed past days of current month up to today
    for day in range(1, today.day + 1):
        cur_date = datetime.date(year, month, day)
        if cur_date.weekday() >= 5:
            # Weekend
            DailyTimeRecord.objects.get_or_create(
                teacher=teacher,
                date=cur_date,
                defaults={'status': DailyTimeRecord.Status.WEEKEND}
            )
            continue

        # Weekday punch
        # 85% On Time, 10% Late, 5% Leave
        roll = random.random()
        if roll < 0.05:
            # On Leave
            DailyTimeRecord.objects.get_or_create(
                teacher=teacher,
                date=cur_date,
                defaults={
                    'status': DailyTimeRecord.Status.ON_LEAVE,
                    'remarks': 'Approved Special Privilege Leave'
                }
            )
        elif roll < 0.15:
            # Late
            am_in = datetime.time(8, random.randint(18, 35))
            rec, _ = DailyTimeRecord.objects.get_or_create(
                teacher=teacher,
                date=cur_date,
                defaults={
                    'am_time_in': am_in,
                    'am_time_out': datetime.time(12, 0),
                    'pm_time_in': datetime.time(13, 0),
                    'pm_time_out': datetime.time(17, random.randint(0, 15)),
                }
            )
            rec.recalculate(shift)
            rec.save()
        else:
            # On Time
            am_in = datetime.time(7, random.randint(45, 58))
            rec, _ = DailyTimeRecord.objects.get_or_create(
                teacher=teacher,
                date=cur_date,
                defaults={
                    'am_time_in': am_in,
                    'am_time_out': datetime.time(12, 0),
                    'pm_time_in': datetime.time(12, random.randint(52, 59)),
                    'pm_time_out': datetime.time(17, random.randint(2, 25)),
                }
            )
            rec.recalculate(shift)
            rec.save()

    # Seed sample Leave Applications
    LeaveApplication.objects.get_or_create(
        teacher=teacher,
        leave_type=LeaveApplication.LeaveType.SPL,
        start_date=datetime.date(year, month, max(1, today.day - 3)),
        end_date=datetime.date(year, month, max(1, today.day - 3)),
        defaults={
            'days_applied': 1.0,
            'reason': 'Family emergency / personal milestone celebration',
            'status': LeaveApplication.Status.APPROVED,
            'reviewed_by': admin_user,
            'reviewed_at': datetime.datetime.now(),
            'admin_remarks': 'Approved per CSC MC No. 41 regulations.',
        }
    )

    LeaveApplication.objects.get_or_create(
        teacher=teacher,
        leave_type=LeaveApplication.LeaveType.VACATION,
        start_date=today + datetime.timedelta(days=7),
        end_date=today + datetime.timedelta(days=8),
        defaults={
            'days_applied': 2.0,
            'reason': 'Scheduled annual rest and family trip',
            'status': LeaveApplication.Status.PENDING,
        }
    )

print(f"Successfully seeded Time & Attendance records for {teachers.count()} teachers.")
