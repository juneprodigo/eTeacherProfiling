"""
pds/models.py — CS Form No. 212 (Revised 2026) Personal Data Sheet Models
Covers all sections: I-VIII + Government Questions + References + Declaration
"""
from django.db import models
from django.conf import settings


# ─────────────────────────────────────────────────────────────────────────────
# ROOT — Teacher Profile
# ─────────────────────────────────────────────────────────────────────────────

class Teacher(models.Model):
    """Central Teacher profile linked to a system user."""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='teacher_profile'
    )
    employee_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    department = models.CharField(max_length=200, blank=True, default='')
    position = models.CharField(max_length=200, blank=True, default='')
    pds_complete = models.BooleanField(default=False)
    photo = models.ImageField(upload_to='teacher_photos/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'pds_teacher'
        ordering = ['user__last_name', 'user__first_name']

    def __str__(self):
        return f'{self.user.get_full_name()} — Teacher Profile'

    def check_pds_completeness(self):
        """Update pds_complete flag based on section fill status."""
        has_personal = hasattr(self, 'personal_info')
        has_family = hasattr(self, 'family_background')
        has_education = self.educational_backgrounds.exists()
        self.pds_complete = all([has_personal, has_family, has_education])
        self.save(update_fields=['pds_complete'])


# ─────────────────────────────────────────────────────────────────────────────
# SECTION I — Personal Information (Items 1–21)
# ─────────────────────────────────────────────────────────────────────────────

class PersonalInfo(models.Model):
    class SexAtBirth(models.TextChoices):
        MALE = 'Male', 'Male'
        FEMALE = 'Female', 'Female'

    class CivilStatus(models.TextChoices):
        SINGLE = 'Single', 'Single'
        MARRIED = 'Married', 'Married'
        WIDOWED = 'Widow/er', 'Widow/er'
        SEPARATED = 'Separated', 'Separated'
        SOLO_PARENT = 'Solo Parent', 'Solo Parent'
        OTHERS = 'Others', 'Others'

    class BloodType(models.TextChoices):
        A_POS = 'A+', 'A+'
        A_NEG = 'A-', 'A-'
        B_POS = 'B+', 'B+'
        B_NEG = 'B-', 'B-'
        AB_POS = 'AB+', 'AB+'
        AB_NEG = 'AB-', 'AB-'
        O_POS = 'O+', 'O+'
        O_NEG = 'O-', 'O-'

    teacher = models.OneToOneField(Teacher, on_delete=models.CASCADE, related_name='personal_info')

    # Item 1–2: Name
    surname = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, default='')
    name_extension = models.CharField(max_length=20, blank=True, default='', help_text='JR., SR., III, etc.')

    # Item 3: Date of Birth
    date_of_birth = models.DateField(null=True, blank=True)

    # Item 4: Place of Birth
    place_of_birth = models.CharField(max_length=255, blank=True, default='')

    # Item 5: Sex at Birth
    sex_at_birth = models.CharField(max_length=10, choices=SexAtBirth.choices, blank=True, default='')

    # Item 6: Civil Status
    civil_status = models.CharField(max_length=20, choices=CivilStatus.choices, blank=True, default='')
    civil_status_others = models.CharField(max_length=100, blank=True, default='')

    # Item 7–9: Physical
    height_m = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, help_text='Height in meters')
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text='Weight in kg')
    blood_type = models.CharField(max_length=5, choices=BloodType.choices, blank=True, default='')

    # Item 10–15: Government IDs
    umid_id_no = models.CharField(max_length=100, blank=True, default='', verbose_name='UMID ID No.')
    pag_ibig_id_no = models.CharField(max_length=100, blank=True, default='', verbose_name='Pag-IBIG ID No.')
    philhealth_no = models.CharField(max_length=100, blank=True, default='', verbose_name='PhilHealth No.')
    philsys_pcn = models.CharField(max_length=100, blank=True, default='', verbose_name='PhilSys Card Number (PCN)')
    tin_no = models.CharField(max_length=100, blank=True, default='', verbose_name='TIN No.')
    agency_employee_no = models.CharField(max_length=100, blank=True, default='')

    # Item 16: Citizenship
    citizenship_filipino = models.BooleanField(default=True)
    dual_citizenship = models.BooleanField(default=False)
    dual_citizenship_country = models.CharField(max_length=100, blank=True, default='')
    dual_citizenship_by_birth = models.BooleanField(default=False)
    dual_citizenship_by_naturalization = models.BooleanField(default=False)

    # Item 17: Residential Address
    res_house_block_lot = models.CharField(max_length=200, blank=True, default='', verbose_name='House/Block/Lot No.')
    res_street = models.CharField(max_length=200, blank=True, default='')
    res_subdivision_village = models.CharField(max_length=200, blank=True, default='')
    res_barangay = models.CharField(max_length=200, blank=True, default='')
    res_city_municipality = models.CharField(max_length=200, blank=True, default='')
    res_province = models.CharField(max_length=200, blank=True, default='')
    res_zip_code = models.CharField(max_length=10, blank=True, default='')

    # Item 18: Permanent Address
    perm_house_block_lot = models.CharField(max_length=200, blank=True, default='', verbose_name='House/Block/Lot No.')
    perm_street = models.CharField(max_length=200, blank=True, default='')
    perm_subdivision_village = models.CharField(max_length=200, blank=True, default='')
    perm_barangay = models.CharField(max_length=200, blank=True, default='')
    perm_city_municipality = models.CharField(max_length=200, blank=True, default='')
    perm_province = models.CharField(max_length=200, blank=True, default='')
    perm_zip_code = models.CharField(max_length=10, blank=True, default='')

    # Items 19–21: Contact
    telephone_no = models.CharField(max_length=50, blank=True, default='')
    mobile_no = models.CharField(max_length=50, blank=True, default='')
    email_address = models.EmailField(blank=True, default='')

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'pds_personal_info'
        verbose_name = 'Personal Information'

    def __str__(self):
        return f'Personal Info — {self.teacher}'


# ─────────────────────────────────────────────────────────────────────────────
# SECTION II — Family Background (Items 22–25)
# ─────────────────────────────────────────────────────────────────────────────

class FamilyBackground(models.Model):
    teacher = models.OneToOneField(Teacher, on_delete=models.CASCADE, related_name='family_background')

    # Item 22: Spouse
    spouse_surname = models.CharField(max_length=100, blank=True, default='')
    spouse_first_name = models.CharField(max_length=100, blank=True, default='')
    spouse_middle_name = models.CharField(max_length=100, blank=True, default='')
    spouse_name_extension = models.CharField(max_length=20, blank=True, default='')
    spouse_occupation = models.CharField(max_length=200, blank=True, default='')
    spouse_employer_business_name = models.CharField(max_length=255, blank=True, default='')
    spouse_business_address = models.TextField(blank=True, default='')
    spouse_telephone_no = models.CharField(max_length=50, blank=True, default='')

    # Item 24: Father
    father_surname = models.CharField(max_length=100, blank=True, default='')
    father_first_name = models.CharField(max_length=100, blank=True, default='')
    father_middle_name = models.CharField(max_length=100, blank=True, default='')
    father_name_extension = models.CharField(max_length=20, blank=True, default='')

    # Item 25: Mother's Maiden Name
    mother_surname = models.CharField(max_length=100, blank=True, default='')
    mother_first_name = models.CharField(max_length=100, blank=True, default='')
    mother_middle_name = models.CharField(max_length=100, blank=True, default='')

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'pds_family_background'
        verbose_name = 'Family Background'

    def __str__(self):
        return f'Family Background — {self.teacher}'


class ChildInfo(models.Model):
    """Item 23: Children (linked to FamilyBackground)"""
    family_background = models.ForeignKey(
        FamilyBackground, on_delete=models.CASCADE, related_name='children'
    )
    name = models.CharField(max_length=255)
    date_of_birth = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'pds_child_info'
        ordering = ['date_of_birth']
        verbose_name = 'Child Information'

    def __str__(self):
        return self.name


# ─────────────────────────────────────────────────────────────────────────────
# SECTION III — Educational Background (Item 26)
# ─────────────────────────────────────────────────────────────────────────────

class EducationalBackground(models.Model):
    class Level(models.TextChoices):
        ELEMENTARY = 'Elementary', 'Elementary'
        SECONDARY = 'Secondary', 'Secondary'
        VOCATIONAL = 'Vocational/Trade Course', 'Vocational/Trade Course'
        COLLEGE = 'College', 'College'
        GRADUATE = 'Graduate Studies', 'Graduate Studies'

    teacher = models.ForeignKey(
        Teacher, on_delete=models.CASCADE, related_name='educational_backgrounds'
    )
    level = models.CharField(max_length=30, choices=Level.choices)
    school_name = models.CharField(max_length=500)
    degree_course = models.CharField(max_length=500, blank=True, default='')
    from_year = models.CharField(max_length=4, blank=True, default='')
    to_year = models.CharField(max_length=4, blank=True, default='')
    highest_level_units_earned = models.CharField(max_length=100, blank=True, default='')
    year_graduated = models.CharField(max_length=4, blank=True, default='')
    scholarship_academic_honors = models.CharField(max_length=500, blank=True, default='')

    class Meta:
        db_table = 'pds_educational_background'
        ordering = ['level']
        verbose_name = 'Educational Background'

    def __str__(self):
        return f'{self.level} — {self.school_name}'


# ─────────────────────────────────────────────────────────────────────────────
# SECTION IV — Civil Service Eligibility (Item 27)
# ─────────────────────────────────────────────────────────────────────────────

class CivilServiceEligibility(models.Model):
    teacher = models.ForeignKey(
        Teacher, on_delete=models.CASCADE, related_name='civil_service_eligibilities'
    )
    eligibility_type = models.CharField(
        max_length=500,
        help_text='Career Service/RA 1080/Board/Bar/CES/CSEE/Barangay/Driver\'s License'
    )
    rating = models.CharField(max_length=50, blank=True, default='', help_text='If Applicable')
    examination_date = models.DateField(null=True, blank=True)
    examination_place = models.CharField(max_length=500, blank=True, default='')
    license_number = models.CharField(max_length=100, blank=True, default='')
    license_validity_date = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'pds_civil_service_eligibility'
        verbose_name = 'Civil Service Eligibility'

    def __str__(self):
        return f'{self.eligibility_type} — {self.teacher}'


# ─────────────────────────────────────────────────────────────────────────────
# SECTION V — Work Experience (Item 28)
# ─────────────────────────────────────────────────────────────────────────────

class WorkExperience(models.Model):
    class AppointmentStatus(models.TextChoices):
        PERMANENT = 'Permanent', 'Permanent'
        TEMPORARY = 'Temporary', 'Temporary'
        CASUAL = 'Casual', 'Casual'
        CONTRACTUAL = 'Contractual', 'Contractual'
        COTERMINOUS = 'Coterminous', 'Coterminous'
        JOB_ORDER = 'Job Order', 'Job Order'
        ELECTED = 'Elected', 'Elected'

    teacher = models.ForeignKey(
        Teacher, on_delete=models.CASCADE, related_name='work_experiences'
    )
    from_date = models.DateField(null=True, blank=True)
    to_date = models.DateField(null=True, blank=True)
    to_present = models.BooleanField(default=False, help_text='Currently working here')
    position_title = models.CharField(max_length=500)
    department_agency_company = models.CharField(max_length=500)
    monthly_salary = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    salary_grade = models.CharField(max_length=20, blank=True, default='', help_text='Format: 00-0')
    appointment_status = models.CharField(
        max_length=30, choices=AppointmentStatus.choices, blank=True, default=''
    )
    is_government_service = models.BooleanField(null=True, blank=True, verbose_name='Government Service (Y/N)')

    class Meta:
        db_table = 'pds_work_experience'
        ordering = ['-from_date']
        verbose_name = 'Work Experience'

    def __str__(self):
        return f'{self.position_title} @ {self.department_agency_company}'


# ─────────────────────────────────────────────────────────────────────────────
# SECTION VI — Learning & Development (Item 29)
# ─────────────────────────────────────────────────────────────────────────────

class LearningDevelopment(models.Model):
    class LDType(models.TextChoices):
        MANAGERIAL = 'Managerial', 'Managerial'
        SUPERVISORY = 'Supervisory', 'Supervisory'
        TECHNICAL = 'Technical', 'Technical'
        FOUNDATIONAL = 'Foundational', 'Foundational'
        CROSS_CUTTING = 'Cross-Cutting', 'Cross-Cutting'

    teacher = models.ForeignKey(
        Teacher, on_delete=models.CASCADE, related_name='learning_developments'
    )
    training_title = models.CharField(max_length=1000)
    from_date = models.DateField(null=True, blank=True)
    to_date = models.DateField(null=True, blank=True)
    number_of_hours = models.PositiveIntegerField(null=True, blank=True)
    ld_type = models.CharField(max_length=30, choices=LDType.choices, blank=True, default='')
    conducted_sponsored_by = models.CharField(max_length=500, blank=True, default='')

    class Meta:
        db_table = 'pds_learning_development'
        ordering = ['-from_date']
        verbose_name = 'Learning and Development'

    def __str__(self):
        return self.training_title


# ─────────────────────────────────────────────────────────────────────────────
# SECTION VII — Voluntary Work (Item 30)
# ─────────────────────────────────────────────────────────────────────────────

class VoluntaryWork(models.Model):
    teacher = models.ForeignKey(
        Teacher, on_delete=models.CASCADE, related_name='voluntary_works'
    )
    organization_name_address = models.TextField()
    from_date = models.DateField(null=True, blank=True)
    to_date = models.DateField(null=True, blank=True)
    number_of_hours = models.PositiveIntegerField(null=True, blank=True)
    position_nature_of_work = models.CharField(max_length=500, blank=True, default='')

    class Meta:
        db_table = 'pds_voluntary_work'
        ordering = ['-from_date']
        verbose_name = 'Voluntary Work'

    def __str__(self):
        return f'{self.organization_name_address[:60]}'


# ─────────────────────────────────────────────────────────────────────────────
# SECTION VIII — Other Information (Items 31–33)
# ─────────────────────────────────────────────────────────────────────────────

class OtherInformation(models.Model):
    teacher = models.OneToOneField(
        Teacher, on_delete=models.CASCADE, related_name='other_information'
    )
    # Item 31
    special_skills_hobbies = models.JSONField(default=list, blank=True)
    # Item 32
    non_academic_distinctions = models.JSONField(default=list, blank=True)
    # Item 33
    organization_memberships = models.JSONField(default=list, blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'pds_other_information'
        verbose_name = 'Other Information'

    def __str__(self):
        return f'Other Info — {self.teacher}'


# ─────────────────────────────────────────────────────────────────────────────
# Government Questions (Items 34–40)
# ─────────────────────────────────────────────────────────────────────────────

class GovernmentQuestions(models.Model):
    teacher = models.OneToOneField(
        Teacher, on_delete=models.CASCADE, related_name='government_questions'
    )

    # Item 34a
    q34a_related_third_degree = models.BooleanField(null=True, blank=True)
    q34a_details = models.TextField(blank=True, default='')
    # Item 34b
    q34b_related_fourth_degree = models.BooleanField(null=True, blank=True)
    q34b_details = models.TextField(blank=True, default='')

    # Item 35a
    q35a_admin_offense = models.BooleanField(null=True, blank=True)
    q35a_details = models.TextField(blank=True, default='')
    # Item 35b
    q35b_criminal_charged = models.BooleanField(null=True, blank=True)
    q35b_date_filed = models.DateField(null=True, blank=True)
    q35b_status = models.TextField(blank=True, default='')
    q35b_details = models.TextField(blank=True, default='')

    # Item 36
    q36_convicted = models.BooleanField(null=True, blank=True)
    q36_details = models.TextField(blank=True, default='')

    # Item 37
    q37_separated_service = models.BooleanField(null=True, blank=True)
    q37_details = models.TextField(blank=True, default='')

    # Item 38a
    q38a_candidate_election = models.BooleanField(null=True, blank=True)
    q38a_details = models.TextField(blank=True, default='')
    # Item 38b
    q38b_resigned_campaign = models.BooleanField(null=True, blank=True)
    q38b_details = models.TextField(blank=True, default='')

    # Item 39
    q39_immigrant_permanent_resident = models.BooleanField(null=True, blank=True)
    q39_country = models.CharField(max_length=100, blank=True, default='')

    # Item 40a
    q40a_indigenous_group = models.BooleanField(null=True, blank=True)
    q40a_specify = models.CharField(max_length=200, blank=True, default='')
    # Item 40b
    q40b_person_with_disability = models.BooleanField(null=True, blank=True)
    q40b_id_number = models.CharField(max_length=100, blank=True, default='')
    # Item 40c
    q40c_solo_parent = models.BooleanField(null=True, blank=True)
    q40c_id_number = models.CharField(max_length=100, blank=True, default='')

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'pds_government_questions'
        verbose_name = 'Government Questions'

    def __str__(self):
        return f'Gov\'t Questions — {self.teacher}'


# ─────────────────────────────────────────────────────────────────────────────
# Item 41 — References
# ─────────────────────────────────────────────────────────────────────────────

class Reference(models.Model):
    teacher = models.ForeignKey(
        Teacher, on_delete=models.CASCADE, related_name='references'
    )
    name = models.CharField(max_length=255)
    office_residential_address = models.TextField(blank=True, default='')
    contact_no_email = models.CharField(max_length=255, blank=True, default='')

    class Meta:
        db_table = 'pds_reference'
        ordering = ['name']
        verbose_name = 'Reference'

    def __str__(self):
        return self.name


# ─────────────────────────────────────────────────────────────────────────────
# Item 42 — PDS Declaration
# ─────────────────────────────────────────────────────────────────────────────

class PDSDeclaration(models.Model):
    teacher = models.OneToOneField(
        Teacher, on_delete=models.CASCADE, related_name='pds_declaration'
    )
    government_id_type = models.CharField(max_length=200, blank=True, default='')
    id_license_passport_no = models.CharField(max_length=200, blank=True, default='')
    date_place_of_issuance = models.CharField(max_length=200, blank=True, default='')
    date_accomplished = models.DateField(null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'pds_declaration'
        verbose_name = 'PDS Declaration'

    def __str__(self):
        return f'Declaration — {self.teacher}'
