from decimal import Decimal
from datetime import date
from django.core.management.base import BaseCommand
from nosi.models import StepIncrementSalarySchedule, StepIncrementRecord
from pds.models import Teacher, WorkExperience
from nosi.services import refresh_smart_alerts


# Standard DepEd Salary Standardization Law (SSL) Table (SG 11 to SG 24, Steps 1 to 8)
SSL_SCHEDULE_DATA = {
    11: [27000, 27284, 27571, 27861, 28154, 28451, 28751, 29054],  # Teacher I
    12: [29165, 29443, 29723, 30006, 30292, 30580, 30872, 31166],  # Teacher II
    13: [31320, 31622, 31927, 32235, 32546, 32860, 33177, 33498],  # Teacher III
    14: [33843, 34185, 34530, 34879, 35232, 35588, 35948, 36311],  # Special Education Teacher I
    15: [36619, 37005, 37395, 37789, 38187, 38589, 38995, 39405],  # Special Education Teacher II
    16: [39672, 40107, 40547, 40992, 41442, 41896, 42356, 42820],  # Special Education Teacher III
    18: [46725, 47285, 47852, 48425, 49004, 49591, 50184, 50784],  # Master Teacher I
    19: [51357, 52024, 52700, 53385, 54079, 54782, 55494, 56216],  # Master Teacher II
    20: [57347, 58156, 58977, 59809, 60653, 61509, 62377, 63257],  # Master Teacher III
    21: [63997, 64969, 65955, 66956, 67972, 69003, 70049, 71110],  # Master Teacher IV / Head Teacher VI
    22: [71511, 72671, 73849, 75045, 76260, 77494, 78747, 80020],  # Principal I
    23: [80003, 81379, 82780, 84206, 85657, 87134, 88637, 90167],  # Principal II
}


class Command(BaseCommand):
    help = 'Seeds DepEd Salary Schedule (Steps 1 to 8) and creates sample NOSI demo records and alerts'

    def handle(self, *args, **options):
        self.stdout.write('Seeding DepEd Salary Schedule...')
        count = 0
        for sg, steps in SSL_SCHEDULE_DATA.items():
            for step_num, amt in enumerate(steps, start=1):
                _, created = StepIncrementSalarySchedule.objects.get_or_create(
                    tranche='DepEd SSL (Fourth Tranche)',
                    salary_grade=sg,
                    step=step_num,
                    defaults={'monthly_salary': Decimal(str(amt))}
                )
                if created:
                    count += 1
        self.stdout.write(self.style.SUCCESS(f'Created {count} Salary Schedule Step items.'))

        # Check Teachers
        teachers = Teacher.objects.all()
        if teachers.exists():
            juan = teachers.filter(user__last_name__icontains='Cruz').first() or teachers.first()

            # Ensure Juan has an existing work record with backdated start to demonstrate upcoming/due NOSI
            work = juan.work_experiences.filter(to_present=True).first()
            if not work:
                work = WorkExperience.objects.create(
                    teacher=juan,
                    from_date=date(2023, 7, 1),
                    to_present=True,
                    position_title="Teacher III",
                    department_agency_company="Department of Education - Division of Isabela",
                    monthly_salary=Decimal('31320.00'),
                    salary_grade="13-1",
                    appointment_status="Permanent",
                    is_government_service=True
                )
            else:
                work.from_date = date(2023, 7, 1)
                work.salary_grade = "13-1"
                work.monthly_salary = Decimal('31320.00')
                work.is_government_service = True
                work.save()

            # Create sample NOSI record for Juan Dela Cruz
            record, r_created = StepIncrementRecord.objects.get_or_create(
                teacher=juan,
                nosi_number="NOSI-2026-07-0012",
                defaults={
                    'basis': StepIncrementRecord.IncrementBasis.LENGTH_OF_SERVICE,
                    'status': StepIncrementRecord.Status.ELIGIBLE_PENDING,
                    'date_issued': date(2026, 7, 1),
                    'effective_date': date(2026, 7, 1),
                    'previous_salary_grade': 13,
                    'previous_step': 1,
                    'previous_monthly_salary': Decimal('31320.00'),
                    'new_salary_grade': 13,
                    'new_step': 2,
                    'new_monthly_salary': Decimal('31622.00'),
                    'monthly_differential': Decimal('302.00'),
                    'division_office': 'Schools Division Office of Isabela',
                    'school_name': 'Naguilian Elementary School',
                    'schools_division_superintendent': 'MADELYN L. MACALLING, PhD, CESO VI',
                    # Check partial requirements for demo
                    'has_approved_nosi': True,
                    'has_annex_d': True,
                    'has_payslips': False,
                    'has_latest_appointment': True,
                    'has_updated_service_record': False,
                    'remarks': 'For completion of Payslips and Updated Service Record.'
                }
            )
            if r_created:
                self.stdout.write(self.style.SUCCESS(f'Created demo Step Increment Record for {juan.user.get_full_name()}'))

        # Run alert generator
        new_alerts = refresh_smart_alerts()
        self.stdout.write(self.style.SUCCESS(f'Smart Alert Engine ran: {new_alerts} alerts generated.'))
