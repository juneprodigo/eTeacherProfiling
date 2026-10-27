import re
from datetime import date, timedelta
from decimal import Decimal
from django.utils import timezone
from pds.models import Teacher, WorkExperience
from .models import StepIncrementRecord, StepIncrementSalarySchedule, NosiAlert


def add_years(d, years):
    """Safely adds years to a date handling leap years."""
    try:
        return d.replace(year=d.year + years)
    except ValueError:
        return d + (date(d.year + years, 3, 1) - date(d.year, 3, 1))


def parse_salary_grade(sg_str):
    """
    Parses '11-1' or '11' or 'SG 11, Step 1' to (grade, step).
    """
    if not sg_str:
        return 11, 1
    match = re.search(r'(\d+)\s*[-/,\s]\s*(\d+)', str(sg_str))
    if match:
        return int(match.group(1)), int(match.group(2))
    digits = re.findall(r'\d+', str(sg_str))
    if digits:
        return int(digits[0]), 1
    return 11, 1


def lookup_salary(salary_grade, step):
    """
    Looks up monthly salary from StepIncrementSalarySchedule table, or falls back to standardized SSL curve.
    """
    schedule_entry = StepIncrementSalarySchedule.objects.filter(salary_grade=salary_grade, step=step).first()
    if schedule_entry:
        return schedule_entry.monthly_salary

    # Standard default baseline calculation if table not yet populated (DepEd SSL SG 11 Base = ~27,000 + increments)
    base_salaries = {
        10: 23176,
        11: 27000,
        12: 29165,
        13: 31320,
        14: 33843,
        15: 36619,
        16: 39672,
        17: 43030,
        18: 46725,
        19: 51357,
        20: 57347,
        21: 63997,
        22: 71511,
    }
    base = base_salaries.get(salary_grade, 27000)
    # Approx 1% - 1.5% increase per step
    step_diff = (step - 1) * (base * 0.012)
    return Decimal(str(round(base + step_diff, 2)))


def calculate_teacher_step_eligibility(teacher, target_date=None):
    """
    Calculates step increment eligibility based on DepEd rules:
    - 1 step increment is granted every 3 years of continuous satisfactory government service.
    - Evaluates work experience entries or latest appointment date.
    - Evaluates existing StepIncrementRecords to find the last step granted.
    """
    if target_date is None:
        target_date = date.today()

    # Find earliest government service or primary appointment
    gov_works = teacher.work_experiences.filter(is_government_service=True).order_by('from_date')
    if not gov_works.exists():
        gov_works = teacher.work_experiences.all().order_by('from_date')

    # Latest current active appointment
    current_work = teacher.work_experiences.filter(to_present=True).first() or teacher.work_experiences.order_by('-from_date').first()

    current_sg = 11
    current_step = 1
    current_salary = Decimal('27000.00')

    if current_work:
        sg, st = parse_salary_grade(current_work.salary_grade)
        current_sg = sg
        current_step = st
        if current_work.monthly_salary:
            current_salary = current_work.monthly_salary
        else:
            current_salary = lookup_salary(current_sg, current_step)

    # Latest recorded NOSI record
    last_record = teacher.step_increments.order_by('-effective_date').first()
    if last_record:
        current_sg = last_record.new_salary_grade
        current_step = last_record.new_step
        current_salary = last_record.new_monthly_salary
        last_effective = last_record.effective_date
    elif gov_works.exists() and gov_works.first().from_date:
        last_effective = gov_works.first().from_date
    else:
        # Fallback to teacher account created date
        last_effective = teacher.created_at.date()

    # Next step date is 3 years after last effective increment
    next_step_date = add_years(last_effective, 3)
    next_step = min(8, current_step + 1)
    next_salary = lookup_salary(current_sg, next_step)

    days_until_due = (next_step_date - target_date).days
    is_due = days_until_due <= 0
    is_upcoming_90_days = 0 < days_until_due <= 90

    return {
        'teacher_id': teacher.id,
        'teacher_name': teacher.user.get_full_name() or teacher.user.username,
        'department': teacher.department or 'DepEd Faculty',
        'position': teacher.position or (current_work.position_title if current_work else 'Teacher I'),
        'current_salary_grade': current_sg,
        'current_step': current_step,
        'current_monthly_salary': current_salary,
        'next_step': next_step,
        'next_salary_grade': current_sg,
        'next_monthly_salary': next_salary,
        'monthly_differential': max(Decimal('0.00'), next_salary - current_salary),
        'last_step_date': last_effective,
        'next_step_date': next_step_date,
        'days_until_due': days_until_due,
        'is_due': is_due,
        'is_upcoming_90_days': is_upcoming_90_days,
        'status_summary': 'OVERDUE' if days_until_due < 0 else ('DUE_NOW' if days_until_due == 0 else ('UPCOMING' if days_until_due <= 90 else 'ON_TRACK')),
        'has_maxed_step': current_step >= 8,
    }


def refresh_smart_alerts():
    """
    Scans all teachers and generates/updates smart notifications and alerts for:
    - Step increments due or coming up within 90/60/30 days
    - Overdue step increments
    - Missing required processing documents on active records
    """
    today = date.today()
    teachers = Teacher.objects.select_related('user').all()

    alerts_created = 0

    for teacher in teachers:
        eligibility = calculate_teacher_step_eligibility(teacher, today)

        # 1. Check if eligible / upcoming / overdue
        if not eligibility['has_maxed_step']:
            days = eligibility['days_until_due']
            next_date = eligibility['next_step_date']
            t_name = eligibility['teacher_name']

            if days <= 0:
                # Overdue or Due Now
                title = f"Notice of Step Increment Due for {t_name}"
                message = (
                    f"{t_name} is entitled to Step Increment (Step {eligibility['current_step']} -> Step {eligibility['next_step']}) "
                    f"effective {next_date.strftime('%B %d, %Y')} ({abs(days)} days ago). "
                    f"Please prepare the DepEd NOSI, verify Key Requirements (Approved NOSI, Annex D, Payslips, Latest Appointment, Updated Service Record), and submit for salary differential processing."
                )
                severity = 'DANGER' if days < -30 else 'WARNING'
                alert_type = 'OVERDUE_INCREMENT' if days < 0 else 'UPCOMING_INCREMENT'

                # Avoid duplicate unread alerts within 15 days
                existing = NosiAlert.objects.filter(
                    teacher=teacher, alert_type=alert_type, is_read=False,
                    created_at__gte=timezone.now() - timedelta(days=15)
                ).first()

                if not existing:
                    NosiAlert.objects.create(
                        teacher=teacher,
                        alert_type=alert_type,
                        severity=severity,
                        title=title,
                        message=message
                    )
                    alerts_created += 1

            elif days <= 90:
                # Upcoming within 90 days
                title = f"Upcoming Step Increment in {days} Days: {t_name}"
                message = (
                    f"{t_name} is reaching the 3-year service period on {next_date.strftime('%B %d, %Y')}. "
                    f"Prepare documentation early: Secure updated Service Record, verify Latest Appointment, and prepare Annex D."
                )
                severity = 'WARNING' if days <= 30 else 'INFO'

                existing = NosiAlert.objects.filter(
                    teacher=teacher, alert_type='UPCOMING_INCREMENT', is_read=False,
                    created_at__gte=timezone.now() - timedelta(days=15)
                ).first()

                if not existing:
                    NosiAlert.objects.create(
                        teacher=teacher,
                        alert_type='UPCOMING_INCREMENT',
                        severity=severity,
                        title=title,
                        message=message
                    )
                    alerts_created += 1

        # 2. Check active records with missing documents
        active_records = teacher.step_increments.exclude(status='INTEGRATED_PAYROLL')
        for rec in active_records:
            missing = []
            if not rec.has_approved_nosi:
                missing.append('Approved NOSI')
            if not rec.has_annex_d:
                missing.append('Annex D / Relevant forms')
            if not rec.has_payslips:
                missing.append('Payslips / Payroll records (before & after)')
            if not rec.has_latest_appointment:
                missing.append('Latest Appointment')
            if not rec.has_updated_service_record:
                missing.append('Updated Service Record')

            if missing:
                existing_missing = NosiAlert.objects.filter(
                    teacher=teacher, record=rec, alert_type='MISSING_REQUIREMENTS', is_read=False,
                    created_at__gte=timezone.now() - timedelta(days=10)
                ).first()

                if not existing_missing:
                    NosiAlert.objects.create(
                        teacher=teacher,
                        record=rec,
                        alert_type='MISSING_REQUIREMENTS',
                        severity='WARNING',
                        title=f"Incomplete NOSI Requirements: {rec.nosi_number or 'Step Increment Record'}",
                        message=f"Missing processing requirements for {t_name}: {', '.join(missing)}. Upload or verify these documents to expedite salary adjustment."
                    )
                    alerts_created += 1

    return alerts_created
