"""
seed_libraries.py — Populates standard reference libraries for DepEd/CES:
Civil Service Eligibility, Positions & Work Experience, L&D / Trainings, and Voluntary Works.
"""
from django.core.management.base import BaseCommand
from pds.models import (
    EligibilityLibrary,
    WorkExperienceLibrary,
    TrainingLibrary,
    VoluntaryWorkLibrary,
)


class Command(BaseCommand):
    help = 'Seeds initial reference library records for PDS dropdown sources'

    def handle(self, *args, **options):
        self.stdout.write('Seeding Reference Libraries for CES / DepEd...')

        # 1. Civil Service Eligibilities
        eligibilities = [
            {
                'eligibility_type': "RA 1080 (Board Licensure Examination for Professional Teachers - BLEPT / LET)",
                'exam_place_hint': 'PRC Regional Office II - Tuguegarao City'
            },
            {
                'eligibility_type': "Career Service Professional (CSC-CSP)",
                'exam_place_hint': 'CSC Regional Office No. 2'
            },
            {
                'eligibility_type': "Career Service Subprofessional (CSC-CSSP)",
                'exam_place_hint': 'CSC Regional Office No. 2'
            },
            {
                'eligibility_type': "Career Executive Service Eligibility (CESE)",
                'exam_place_hint': 'Career Executive Service Board (CESB)'
            },
            {
                'eligibility_type': "Career Service Executive Eligibility (CSEE)",
                'exam_place_hint': 'Civil Service Commission Central Office'
            },
            {
                'eligibility_type': "RA 1080 (PRC Registered Professional / Allied Board)",
                'exam_place_hint': 'Professional Regulation Commission'
            },
            {
                'eligibility_type': "Honor Graduate Eligibility (PD 907)",
                'exam_place_hint': 'CSC Regional Office No. 2'
            },
            {
                'eligibility_type': "Barangay Official Eligibility (BOE)",
                'exam_place_hint': 'Civil Service Commission'
            },
            {
                'eligibility_type': "Barangay Health Worker Eligibility (BHWE)",
                'exam_place_hint': 'Civil Service Commission'
            },
            {
                'eligibility_type': "Sanggunian Member Eligibility (SME)",
                'exam_place_hint': 'Civil Service Commission'
            },
            {
                'eligibility_type': "TESDA National Certificate II (NC II)",
                'exam_place_hint': 'TESDA Accredited Assessment Center'
            },
            {
                'eligibility_type': "TESDA National Certificate III (NC III) - Trainer / Assessor",
                'exam_place_hint': 'TESDA Regional Training Center'
            },
            {
                'eligibility_type': "Scientific and Technological Specialist Eligibility (STSE)",
                'exam_place_hint': 'Department of Science and Technology (DOST)'
            },
            {
                'eligibility_type': "Driver's License (Professional / Non-Professional)",
                'exam_place_hint': 'Land Transportation Office (LTO)'
            },
        ]
        created_el = 0
        for item in eligibilities:
            _, created = EligibilityLibrary.objects.get_or_create(
                eligibility_type=item['eligibility_type'],
                defaults={'exam_place_hint': item['exam_place_hint'], 'is_active': True}
            )
            if created:
                created_el += 1
        self.stdout.write(self.style.SUCCESS(f'Eligibilities seeded: {created_el} new records'))

        # 2. Work Experience / Positions
        work_experiences = [
            {
                'position_title': 'Teacher I',
                'department_agency_company': 'Cagayan National High School - DepEd',
                'salary_grade': '11-1',
                'appointment_status': 'Permanent',
                'is_government_service': True
            },
            {
                'position_title': 'Teacher II',
                'department_agency_company': 'Cagayan National High School - DepEd',
                'salary_grade': '12-1',
                'appointment_status': 'Permanent',
                'is_government_service': True
            },
            {
                'position_title': 'Teacher III',
                'department_agency_company': 'Cagayan National High School - DepEd',
                'salary_grade': '13-1',
                'appointment_status': 'Permanent',
                'is_government_service': True
            },
            {
                'position_title': 'Master Teacher I',
                'department_agency_company': 'Cagayan National High School - DepEd',
                'salary_grade': '18-1',
                'appointment_status': 'Permanent',
                'is_government_service': True
            },
            {
                'position_title': 'Master Teacher II',
                'department_agency_company': 'Cagayan National High School - DepEd',
                'salary_grade': '19-1',
                'appointment_status': 'Permanent',
                'is_government_service': True
            },
            {
                'position_title': 'Master Teacher III',
                'department_agency_company': 'Cagayan National High School - DepEd',
                'salary_grade': '20-1',
                'appointment_status': 'Permanent',
                'is_government_service': True
            },
            {
                'position_title': 'Special Science Teacher I',
                'department_agency_company': 'Cagayan National High School - DepEd',
                'salary_grade': '13-1',
                'appointment_status': 'Permanent',
                'is_government_service': True
            },
            {
                'position_title': 'Special Education Teacher I',
                'department_agency_company': 'Department of Education - Division of Tuguegarao City',
                'salary_grade': '14-1',
                'appointment_status': 'Permanent',
                'is_government_service': True
            },
            {
                'position_title': 'Head Teacher I',
                'department_agency_company': 'Cagayan National High School - DepEd',
                'salary_grade': '14-1',
                'appointment_status': 'Permanent',
                'is_government_service': True
            },
            {
                'position_title': 'Head Teacher III',
                'department_agency_company': 'Cagayan National High School - DepEd',
                'salary_grade': '16-1',
                'appointment_status': 'Permanent',
                'is_government_service': True
            },
            {
                'position_title': 'School Principal I',
                'department_agency_company': 'Department of Education - Division Office',
                'salary_grade': '19-1',
                'appointment_status': 'Permanent',
                'is_government_service': True
            },
            {
                'position_title': 'Guidance Counselor I',
                'department_agency_company': 'Cagayan National High School - DepEd',
                'salary_grade': '11-1',
                'appointment_status': 'Permanent',
                'is_government_service': True
            },
            {
                'position_title': 'Administrative Officer II',
                'department_agency_company': 'Cagayan National High School - DepEd',
                'salary_grade': '11-1',
                'appointment_status': 'Permanent',
                'is_government_service': True
            },
            {
                'position_title': 'Administrative Assistant II (Disbursing Officer)',
                'department_agency_company': 'Cagayan National High School - DepEd',
                'salary_grade': '8-1',
                'appointment_status': 'Permanent',
                'is_government_service': True
            },
            {
                'position_title': 'Administrative Assistant III (Senior Bookkeeper)',
                'department_agency_company': 'Cagayan National High School - DepEd',
                'salary_grade': '9-1',
                'appointment_status': 'Permanent',
                'is_government_service': True
            },
            {
                'position_title': 'Substitute Teacher',
                'department_agency_company': 'Department of Education - Division of Tuguegarao City',
                'salary_grade': '11-1',
                'appointment_status': 'Contractual',
                'is_government_service': True
            },
            {
                'position_title': 'College Instructor I',
                'department_agency_company': 'Cagayan State University',
                'salary_grade': '12-1',
                'appointment_status': 'Permanent',
                'is_government_service': True
            },
        ]
        created_we = 0
        for item in work_experiences:
            _, created = WorkExperienceLibrary.objects.get_or_create(
                position_title=item['position_title'],
                department_agency_company=item['department_agency_company'],
                defaults={
                    'salary_grade': item['salary_grade'],
                    'appointment_status': item['appointment_status'],
                    'is_government_service': item['is_government_service'],
                    'is_active': True,
                }
            )
            if created:
                created_we += 1
        self.stdout.write(self.style.SUCCESS(f'Work Experiences seeded: {created_we} new records'))

        # 3. Learning & Development / Trainings
        trainings = [
            {
                'training_title': 'Regional Training-Workshop on the MATATAG Curriculum for Secondary Teachers',
                'ld_type': 'Technical',
                'default_hours': 40,
                'conducted_sponsored_by': 'Department of Education - Regional Office II',
                'description': 'Comprehensive pedagogical orientation on MATATAG curriculum standards and learning competencies.'
            },
            {
                'training_title': 'School Learning Action Cell (SLAC) Sessions on Innovative Pedagogies and Assessment',
                'ld_type': 'Technical',
                'default_hours': 24,
                'conducted_sponsored_by': 'Cagayan National High School',
                'description': 'Continuous professional development sessions for subject area faculty.'
            },
            {
                'training_title': 'Mid-Year In-Service Training for Teachers (INSET)',
                'ld_type': 'Technical',
                'default_hours': 40,
                'conducted_sponsored_by': 'Department of Education - Cagayan National High School',
                'description': 'Institutional capacity building and lesson enhancement workshop.'
            },
            {
                'training_title': 'National Educators Academy of the Philippines (NEAP) Professional Development Program',
                'ld_type': 'Foundational',
                'default_hours': 40,
                'conducted_sponsored_by': 'National Educators Academy of the Philippines (NEAP)',
                'description': 'Standards-based professional development aligned with PPST standards.'
            },
            {
                'training_title': 'Early Language, Literacy, and Numeracy (ELLN) Remediation Strategies',
                'ld_type': 'Technical',
                'default_hours': 32,
                'conducted_sponsored_by': 'Department of Education Central Office',
                'description': 'Strategies for diagnostic literacy instruction and learning recovery.'
            },
            {
                'training_title': 'Action Research in Basic Education Methodology and Manuscript Preparation',
                'ld_type': 'Technical',
                'default_hours': 40,
                'conducted_sponsored_by': 'DepEd Schools Division Office of Tuguegarao City',
                'description': 'BERF-aligned research formulation, data analysis, and publication workshop.'
            },
            {
                'training_title': 'ICT Integration, Learning Management Systems, & Artificial Intelligence in Education',
                'ld_type': 'Technical',
                'default_hours': 32,
                'conducted_sponsored_by': 'DepEd Information and Communications Technology Service (ICTS)',
                'description': 'Harnessing modern educational technology and productivity tools in classrooms.'
            },
            {
                'training_title': 'Child Protection Policy, Positive Discipline, and Anti-Bullying in School Environments',
                'ld_type': 'Foundational',
                'default_hours': 16,
                'conducted_sponsored_by': 'DepEd Legal Affairs / Child Protection Unit',
                'description': 'Legal frameworks and practical strategies for child safety and psychological well-being.'
            },
            {
                'training_title': 'School-Based Disaster Risk Reduction and Management (DRRM) & Standard First Aid',
                'ld_type': 'Technical',
                'default_hours': 24,
                'conducted_sponsored_by': 'DepEd DRRMS / Philippine Red Cross',
                'description': 'Emergency disaster preparedness, earthquake drills, and basic life support for schools.'
            },
            {
                'training_title': 'Instructional Leadership and Supervisory Competence for Master Teachers',
                'ld_type': 'Supervisory',
                'default_hours': 40,
                'conducted_sponsored_by': 'DepEd Human Resource Development Division - Region II',
                'description': 'Classroom observation, technical assistance coaching, and mentoring protocols.'
            },
            {
                'training_title': 'Gender and Development (GAD) Mainstreaming and Inclusive Education Seminar',
                'ld_type': 'Cross-Cutting',
                'default_hours': 16,
                'conducted_sponsored_by': 'DepEd GAD Focal Point System',
                'description': 'Gender-fair education, sensitivity, and inclusive classroom practices.'
            },
        ]
        created_tr = 0
        for item in trainings:
            _, created = TrainingLibrary.objects.get_or_create(
                training_title=item['training_title'],
                defaults={
                    'ld_type': item['ld_type'],
                    'default_hours': item['default_hours'],
                    'conducted_sponsored_by': item['conducted_sponsored_by'],
                    'description': item['description'],
                    'is_active': True,
                }
            )
            if created:
                created_tr += 1
        self.stdout.write(self.style.SUCCESS(f'Trainings seeded: {created_tr} new records'))

        # 4. Voluntary Works / Organizations
        voluntary_works = [
            {
                'organization_name_address': 'Philippine Red Cross - Cagayan Chapter, Tuguegarao City',
                'position_nature_of_work': 'Volunteer First Aider / Blood Program Coordinator',
                'default_hours': 40,
            },
            {
                'organization_name_address': 'Girl Scouts of the Philippines (GSP) - Cagayan Council',
                'position_nature_of_work': 'Troop Leader / District Field Commissioner',
                'default_hours': 50,
            },
            {
                'organization_name_address': 'Boy Scouts of the Philippines (BSP) - Cagayan Council',
                'position_nature_of_work': 'Outfit Advisor / Merit Badge Counselor',
                'default_hours': 50,
            },
            {
                'organization_name_address': 'Parent-Teacher Association (PTA) - Cagayan National High School',
                'position_nature_of_work': 'Faculty Coordinator & Community Liaison Officer',
                'default_hours': 30,
            },
            {
                'organization_name_address': 'Brigada Eskwela Community Volunteers Network - CES',
                'position_nature_of_work': 'Resource Mobilization & Volunteer Team Lead',
                'default_hours': 40,
            },
            {
                'organization_name_address': 'Tuguegarao City Youth Development Alliance',
                'position_nature_of_work': 'Youth Mentor / Community Education Volunteer',
                'default_hours': 24,
            },
            {
                'organization_name_address': 'Parish Pastoral Council for Responsible Voting (PPCRV) - Tuguegarao',
                'position_nature_of_work': 'Volunteer Poll Watcher / Precinct Information Facilitator',
                'default_hours': 16,
            },
            {
                'organization_name_address': 'Rotary Club of Tuguegarao Rainbow Community Outreach',
                'position_nature_of_work': 'Literacy Project Volunteer Coordinator',
                'default_hours': 24,
            },
            {
                'organization_name_address': 'Habitat for Humanity Philippines - Cagayan Chapter',
                'position_nature_of_work': 'Community Shelter Construction Volunteer',
                'default_hours': 32,
            },
        ]
        created_vol = 0
        for item in voluntary_works:
            _, created = VoluntaryWorkLibrary.objects.get_or_create(
                organization_name_address=item['organization_name_address'],
                defaults={
                    'position_nature_of_work': item['position_nature_of_work'],
                    'default_hours': item['default_hours'],
                    'is_active': True,
                }
            )
            if created:
                created_vol += 1
        self.stdout.write(self.style.SUCCESS(f'Voluntary Works seeded: {created_vol} new records'))
        self.stdout.write(self.style.SUCCESS('Successfully completed seeding all CES / DepEd Reference Libraries.'))
