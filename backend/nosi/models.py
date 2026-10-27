import os
from django.db import models
from django.conf import settings
from decimal import Decimal
from pds.models import Teacher


def nosi_document_upload_path(instance, filename):
    return f"nosi_docs/teacher_{instance.record.teacher.id}/{instance.doc_type}_{filename}"


def direct_nosi_document_upload_path(instance, filename):
    return f"nosi_docs/teacher_{instance.teacher.id}/direct_{filename}"


def service_record_document_upload_path(instance, filename):
    return f"service_records/teacher_{instance.teacher.id}/{filename}"


def nosa_document_upload_path(instance, filename):
    return f"nosa_docs/teacher_{instance.teacher.id}/{filename}"


def appointment_document_upload_path(instance, filename):
    return f"appointment_docs/teacher_{instance.teacher.id}/{filename}"


class StepIncrementSalarySchedule(models.Model):
    """
    Standard DepEd / DBM Salary Schedule table per Salary Grade (SG 1 to SG 33) and Steps 1 to 8.
    """
    tranche = models.CharField(max_length=50, default='SSL 2024/2026')
    salary_grade = models.PositiveIntegerField(help_text="e.g. 11 for Teacher I, 12 for Teacher II, 13 for Teacher III, 18 for Master Teacher I")
    step = models.PositiveIntegerField(help_text="Step 1 to 8")
    monthly_salary = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        db_table = 'nosi_salary_schedule'
        unique_together = ('tranche', 'salary_grade', 'step')
        ordering = ['salary_grade', 'step']

    def __str__(self):
        return f"SG {self.salary_grade} - Step {self.step}: ₱{self.monthly_salary:,.2f}"


class StepIncrementRecord(models.Model):
    """
    Main record for a teacher's Step Increment & DepEd NOSI tracking.
    """
    class IncrementBasis(models.TextChoices):
        LENGTH_OF_SERVICE = 'LENGTH_OF_SERVICE', 'Length of Service (Every 3 Years of continuous satisfactory service)'
        MERIT_STEP = 'MERIT', 'Meritorious Performance / Outstanding Achievement'

    class Status(models.TextChoices):
        ELIGIBLE_PENDING = 'ELIGIBLE_PENDING', 'Eligible / For Processing'
        DOCS_INCOMPLETE = 'DOCS_INCOMPLETE', 'Incomplete Requirements'
        DOCS_VERIFIED = 'DOCS_VERIFIED', 'Requirements Complete & Verified'
        NOSI_GENERATED = 'NOSI_GENERATED', 'NOSI Prepared & Generated'
        APPROVED = 'APPROVED', 'Approved by SDS / Appointing Authority'
        INTEGRATED_PAYROLL = 'INTEGRATED_PAYROLL', 'Integrated into Payroll / Differential Paid'

    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='step_increments')
    basis = models.CharField(max_length=30, choices=IncrementBasis.choices, default=IncrementBasis.LENGTH_OF_SERVICE)
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.ELIGIBLE_PENDING)

    # Reference Numbers & Metadata
    nosi_number = models.CharField(max_length=100, blank=True, default='', help_text="e.g. NOSI-2026-SDO-001")
    date_issued = models.DateField(null=True, blank=True)
    effective_date = models.DateField(help_text="Date when increment takes effect (e.g., anniversary date)")
    
    # Previous & New Step details
    previous_salary_grade = models.PositiveIntegerField(default=11)
    previous_step = models.PositiveIntegerField(default=1)
    previous_monthly_salary = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

    new_salary_grade = models.PositiveIntegerField(default=11)
    new_step = models.PositiveIntegerField(default=2)
    new_monthly_salary = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    
    monthly_differential = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

    # Administrative signers
    schools_division_superintendent = models.CharField(max_length=200, blank=True, default='Schools Division Superintendent')
    division_office = models.CharField(max_length=255, blank=True, default='Division of Schools / SDO')
    school_name = models.CharField(max_length=255, blank=True, default='Naguilian Elementary School')

    # Checklist booleans (Key Requirements for Processing)
    has_approved_nosi = models.BooleanField(default=False, verbose_name="Approved NOSI")
    has_annex_d = models.BooleanField(default=False, verbose_name="Annex D / Relevant forms")
    has_payslips = models.BooleanField(default=False, verbose_name="Payslips or payroll records (before and after)")
    has_latest_appointment = models.BooleanField(default=False, verbose_name="Latest Appointment")
    has_updated_service_record = models.BooleanField(default=False, verbose_name="Updated Service Record")

    document_file = models.FileField(upload_to=direct_nosi_document_upload_path, null=True, blank=True)
    remarks = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'nosi_records'
        ordering = ['-effective_date', '-created_at']

    def __str__(self):
        return f"{self.teacher.user.get_full_name()} — Step {self.previous_step} to {self.new_step} (Effective: {self.effective_date})"

    def save(self, *args, **kwargs):
        if self.new_monthly_salary and self.previous_monthly_salary:
            self.monthly_differential = max(Decimal('0.00'), self.new_monthly_salary - self.previous_monthly_salary)
        super().save(*args, **kwargs)


class StepIncrementDocument(models.Model):
    """
    Supporting uploaded documents for NOSI processing requirement verification:
    - Approved NOSI
    - Annex D / Relevant forms
    - Payslips or payroll records (before & after step inclusion)
    - Latest Appointment
    - Updated Service Record
    """
    DOC_TYPES = [
        ('APPROVED_NOSI', 'Approved NOSI'),
        ('ANNEX_D', 'Annex D / Relevant Forms'),
        ('PAYSLIP', 'Payslip / Payroll Record (Before & After Inclusion)'),
        ('LATEST_APPOINTMENT', 'Latest Appointment'),
        ('SERVICE_RECORD', 'Updated Service Record'),
        ('OTHER', 'Other Supporting Document'),
    ]

    record = models.ForeignKey(StepIncrementRecord, on_delete=models.CASCADE, related_name='documents')
    doc_type = models.CharField(max_length=30, choices=DOC_TYPES)
    title = models.CharField(max_length=255, blank=True, default='')
    file = models.FileField(upload_to=nosi_document_upload_path)
    is_verified = models.BooleanField(default=False)
    verification_notes = models.CharField(max_length=255, blank=True, default='')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'nosi_documents'
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.get_doc_type_display()} for {self.record}"


class NosiAlert(models.Model):
    """
    Smart alerts & notification for due / upcoming step increments or missing requirements.
    """
    ALERT_TYPES = [
        ('UPCOMING_INCREMENT', 'Upcoming Step Increment Due (within 90/60/30 days)'),
        ('OVERDUE_INCREMENT', 'Overdue Step Increment Claim'),
        ('MISSING_REQUIREMENTS', 'Missing Key Processing Documents'),
        ('APPROVED_READY', 'Approved NOSI Ready for Differential Processing'),
    ]

    ALERT_SEVERITY = [
        ('INFO', 'Information'),
        ('WARNING', 'Warning / Approaching Due'),
        ('DANGER', 'Overdue / Action Urgently Required'),
        ('SUCCESS', 'Completed / Approved'),
    ]

    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='nosi_alerts')
    record = models.ForeignKey(StepIncrementRecord, on_delete=models.CASCADE, related_name='alerts', null=True, blank=True)
    alert_type = models.CharField(max_length=30, choices=ALERT_TYPES)
    severity = models.CharField(max_length=15, choices=ALERT_SEVERITY, default='INFO')
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'nosi_alerts'
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.severity}] {self.title} - {self.teacher.user.get_full_name()}"


class ServiceRecordEntry(models.Model):
    """
    CSC Form No. 122 — Official Service Record Entry.
    Chronological employment history essential for promotion, retirement, and salary differential claims.
    """
    STATUS_CHOICES = [
        ('Permanent', 'Permanent'),
        ('Provisional', 'Provisional'),
        ('Temporary', 'Temporary'),
        ('Substitute', 'Substitute'),
        ('Contractual', 'Contractual'),
        ('Casual', 'Casual'),
        ('Coterminous', 'Coterminous'),
        ('Job Order', 'Job Order'),
    ]

    BRANCH_CHOICES = [
        ('National', 'National'),
        ('Provincial', 'Provincial'),
        ('Municipal/City (LGU)', 'Municipal/City (LGU)'),
        ('Private', 'Private'),
    ]

    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='service_records')
    from_date = models.DateField(help_text="Start date of inclusive service period")
    to_date = models.DateField(null=True, blank=True, help_text="End date (leave blank if to present)")
    to_present = models.BooleanField(default=False, help_text="Current / ongoing designation")

    designation = models.CharField(max_length=255, help_text="e.g. Teacher I, Teacher II, Master Teacher I")
    status_of_appointment = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Permanent')
    salary_grade = models.PositiveIntegerField(null=True, blank=True, default=11)
    step = models.PositiveIntegerField(null=True, blank=True, default=1)
    monthly_salary = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    annual_salary = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))

    station_office = models.CharField(max_length=255, default='DepEd - Isabela', help_text="Station / School / Office")
    branch = models.CharField(max_length=50, choices=BRANCH_CHOICES, default='National')
    lwop_dates = models.CharField(max_length=255, blank=True, default='NONE', help_text="Leave of Absence Without Pay dates or NONE")
    separation_date = models.DateField(null=True, blank=True)
    separation_cause = models.CharField(max_length=255, blank=True, default='', help_text="e.g. Promotion, Transfer, Retirement, Resigned")
    remarks = models.TextField(blank=True, default='', help_text="e.g. Original Appointment, Step Increment, SSL Adjustment")

    document_file = models.FileField(upload_to=service_record_document_upload_path, null=True, blank=True, help_text="Attached scanned service record document")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'nosi_service_records'
        ordering = ['-from_date', '-id']

    def __str__(self):
        to_str = "Present" if self.to_present else str(self.to_date)
        return f"{self.teacher.user.get_full_name()} — {self.designation} ({self.from_date} to {to_str})"

    def save(self, *args, **kwargs):
        if self.monthly_salary and (not self.annual_salary or self.annual_salary == Decimal('0.00')):
            self.annual_salary = self.monthly_salary * 12
        elif self.annual_salary and (not self.monthly_salary or self.monthly_salary == Decimal('0.00')):
            self.monthly_salary = self.annual_salary / 12
        super().save(*args, **kwargs)


class SalaryAdjustmentRecord(models.Model):
    """
    DepEd Notice of Salary Adjustment (NOSA).
    Issued upon implementation of Salary Standardization Law (SSL) tranches, Executive Orders, or National Budget Circulars.
    """
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('ISSUED', 'Issued'),
        ('APPROVED', 'Approved by SDS'),
        ('INTEGRATED_PAYROLL', 'Integrated into Payroll / Differential Paid'),
    ]

    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='salary_adjustments')
    nosa_number = models.CharField(max_length=100, blank=True, default='', help_text="e.g. NOSA-2024-SDO-001")
    date_issued = models.DateField(null=True, blank=True)
    effective_date = models.DateField(help_text="Effective date of salary adjustment (e.g. 2024-01-01)")
    legal_basis = models.CharField(max_length=255, default='Executive Order No. 64, s. 2024 / NBC No. 594', help_text="Legal authority / mandate")

    position_title = models.CharField(max_length=255, blank=True, default='')
    salary_grade = models.PositiveIntegerField(default=11)
    step = models.PositiveIntegerField(default=1)

    previous_monthly_salary = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    adjusted_monthly_salary = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    monthly_differential = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='ISSUED')
    signatory_authority = models.CharField(max_length=255, default='Schools Division Superintendent')
    remarks = models.TextField(blank=True, default='')

    document_file = models.FileField(upload_to=nosa_document_upload_path, null=True, blank=True, help_text="Scanned copy of signed NOSA")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'nosi_salary_adjustments'
        ordering = ['-effective_date', '-created_at']

    def __str__(self):
        return f"{self.nosa_number or 'NOSA'} — {self.teacher.user.get_full_name()} (SG {self.salary_grade} Step {self.step})"

    def save(self, *args, **kwargs):
        if self.adjusted_monthly_salary and self.previous_monthly_salary:
            self.monthly_differential = max(Decimal('0.00'), self.adjusted_monthly_salary - self.previous_monthly_salary)
        super().save(*args, **kwargs)


class AppointmentRecord(models.Model):
    """
    Civil Service Commission Form No. 33 / KSS Pormularyo Blg. 33 — Official Appointment.
    Tracks official plantilla appointment papers, item numbers, and CSC attestations.
    """
    NATURE_CHOICES = [
        ('Original', 'Original'),
        ('Promotion', 'Promotion'),
        ('Transfer', 'Transfer'),
        ('Reemployment', 'Reemployment'),
        ('Reappointment', 'Reappointment'),
        ('Reclassification', 'Reclassification'),
        ('Demotion', 'Demotion'),
    ]

    STATUS_CHOICES = [
        ('Permanent', 'Permanent'),
        ('Provisional', 'Provisional'),
        ('Temporary', 'Temporary'),
        ('Substitute', 'Substitute'),
        ('Contractual', 'Contractual'),
        ('Coterminous', 'Coterminous'),
    ]

    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='appointments')
    appointment_number = models.CharField(max_length=100, blank=True, default='', help_text="e.g. APPT-2023-018")
    position_title = models.CharField(max_length=255, help_text="e.g. Teacher I, Teacher II, Master Teacher I")
    plantilla_item_no = models.CharField(max_length=100, help_text="DepEd PSI-POP Plantilla Item Number, e.g. TCH1-123456-2020")

    nature_of_appointment = models.CharField(max_length=50, choices=NATURE_CHOICES, default='Original')
    status_of_appointment = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Permanent')

    salary_grade = models.PositiveIntegerField(default=11)
    step = models.PositiveIntegerField(default=1)
    monthly_rate = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    annual_rate = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))

    date_of_signing = models.DateField(null=True, blank=True, help_text="Date signed by Appointing Officer")
    date_of_assumption = models.DateField(null=True, blank=True, help_text="Date entered upon duty / effectivity")
    csc_attestation_date = models.DateField(null=True, blank=True, help_text="Date attested / approved by CSC")
    csc_action = models.CharField(max_length=100, default='Approved / Validated')

    vice_personnel = models.CharField(max_length=255, blank=True, default='', help_text="Former incumbent, or 'Newly Created Item'")
    vice_reason = models.CharField(max_length=100, blank=True, default='', help_text="Transferred / Retired / Resigned / Promoted / Deceased")
    page_no_plantilla = models.CharField(max_length=50, blank=True, default='', help_text="Page in Plantilla")
    remarks = models.TextField(blank=True, default='')

    document_file = models.FileField(upload_to=appointment_document_upload_path, null=True, blank=True, help_text="Scanned CS Form 33 / KSS appointment file")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'nosi_appointments'
        ordering = ['-date_of_assumption', '-date_of_signing', '-created_at']

    def __str__(self):
        return f"{self.position_title} ({self.plantilla_item_no}) — {self.teacher.user.get_full_name()}"

    def save(self, *args, **kwargs):
        if self.monthly_rate and (not self.annual_rate or self.annual_rate == Decimal('0.00')):
            self.annual_rate = self.monthly_rate * 12
        elif self.annual_rate and (not self.monthly_rate or self.monthly_rate == Decimal('0.00')):
            self.monthly_rate = self.annual_rate / 12
        super().save(*args, **kwargs)

