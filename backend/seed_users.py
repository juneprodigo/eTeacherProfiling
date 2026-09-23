import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from pds.models import Teacher, PersonalInfo

User = get_user_model()

# 1. Create Admin
admin_user, created = User.objects.get_or_create(
    username='admin',
    defaults={
        'email': 'admin@ces.deped.gov.ph',
        'first_name': 'System',
        'last_name': 'Administrator',
        'role': 'admin',
        'is_staff': True,
        'is_superuser': True,
    }
)
if created:
    admin_user.set_password('Admin@123456')
    admin_user.save()
    print('Created Admin: admin / Admin@123456')
else:
    print('Admin already exists')

# 2. Create HR Officer
hr_user, created = User.objects.get_or_create(
    username='hr_officer',
    defaults={
        'email': 'hr@ces.deped.gov.ph',
        'first_name': 'Maria',
        'last_name': 'Santos',
        'role': 'hr',
        'is_staff': True,
    }
)
if created:
    hr_user.set_password('Hr@123456')
    hr_user.save()
    print('Created HR Officer: hr_officer / Hr@123456')
else:
    print('HR Officer already exists')

# 3. Create Sample Teacher User & Profile
teacher_user, created = User.objects.get_or_create(
    username='teacher1',
    defaults={
        'email': 'teacher1@ces.deped.gov.ph',
        'first_name': 'Juan',
        'last_name': 'Dela Cruz',
        'role': 'teacher',
    }
)
if created:
    teacher_user.set_password('Teacher@123456')
    teacher_user.save()
    print('Created Teacher: teacher1 / Teacher@123456')

teacher_profile, created = Teacher.objects.get_or_create(
    user=teacher_user,
    defaults={
        'employee_id': 'DEPED-2026-001',
        'department': 'Science Department',
        'position': 'Master Teacher I',
    }
)

if not hasattr(teacher_profile, 'personal_info'):
    PersonalInfo.objects.create(
        teacher=teacher_profile,
        surname='Dela Cruz',
        first_name='Juan',
        middle_name='Protacio',
        name_extension='',
        date_of_birth='1988-06-19',
        place_of_birth='Manila',
        sex_at_birth='Male',
        civil_status='Married',
        citizenship_filipino=True,
        res_city_municipality='Quezon City',
        res_province='Metro Manila',
        mobile_no='09171234567',
        email_address='juan.delacruz@deped.gov.ph',
        agency_employee_no='DEPED-2026-001'
    )
    print('Created default PersonalInfo for teacher1')
