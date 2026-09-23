from django.db import models
from pds.models import Teacher


class SchoolActivity(models.Model):
    class ActivityType(models.TextChoices):
        TRAINING = 'Faculty Development / Training', 'Faculty Development / Training'
        MEETING = 'Faculty & Staff Meeting', 'Faculty & Staff Meeting'
        SEMINAR = 'Institutional Seminar / Workshop', 'Institutional Seminar / Workshop'
        ASSEMBLY = 'School Assembly / Convocation', 'School Assembly / Convocation'
        CURRICULUM = 'Curriculum & Syllabi Review', 'Curriculum & Syllabi Review'
        ACCREDITATION = 'Accreditation & Compliance', 'Accreditation & Compliance'
        EXTENSION = 'Community Extension & Outreach', 'Community Extension & Outreach'
        CO_CURRICULAR = 'Co-Curricular / Student Activity', 'Co-Curricular / Student Activity'
        OTHERS = 'Others', 'Others'

    class Modality(models.TextChoices):
        IN_PERSON = 'In-Person', 'In-Person'
        ONLINE = 'Online / Virtual', 'Online / Virtual'
        HYBRID = 'Hybrid', 'Hybrid'

    class Status(models.TextChoices):
        UPCOMING = 'Upcoming', 'Upcoming'
        IN_PROGRESS = 'In Progress', 'In Progress'
        COMPLETED = 'Completed', 'Completed'
        POSTPONED = 'Postponed', 'Postponed'
        CANCELLED = 'Cancelled', 'Cancelled'

    title = models.CharField(max_length=255)
    activity_type = models.CharField(
        max_length=100, choices=ActivityType.choices, default=ActivityType.TRAINING
    )
    description = models.TextField(blank=True, default='')
    venue = models.CharField(max_length=255, default='Main Campus / School Facility')
    modality = models.CharField(
        max_length=50, choices=Modality.choices, default=Modality.IN_PERSON
    )
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    status = models.CharField(
        max_length=50, choices=Status.choices, default=Status.UPCOMING
    )

    coordinator = models.ForeignKey(
        Teacher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='coordinated_activities',
    )
    budget = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    funding_source = models.CharField(max_length=200, blank=True, default='School MOOE')
    attachment = models.FileField(upload_to='activity_attachments/', null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'school_activity'
        ordering = ['-start_date']
        verbose_name = 'School Activity'
        verbose_name_plural = 'School Activities'

    def __str__(self):
        return f'{self.title} ({self.activity_type})'

    @property
    def participant_count(self):
        return self.participants.count()

    @property
    def attended_count(self):
        return self.participants.filter(attendance_status='Attended').count()


class ActivityParticipant(models.Model):
    class Role(models.TextChoices):
        PARTICIPANT = 'Participant', 'Participant'
        SPEAKER = 'Resource Speaker / Trainer', 'Resource Speaker / Trainer'
        FACILITATOR = 'Facilitator / Committee', 'Facilitator / Committee'
        ORGANIZER = 'Organizer / Coordinator', 'Organizer / Coordinator'

    class AttendanceStatus(models.TextChoices):
        REGISTERED = 'Registered', 'Registered'
        ATTENDED = 'Attended', 'Attended'
        EXCUSED = 'Excused', 'Excused'
        ABSENT = 'Absent', 'Absent'

    activity = models.ForeignKey(
        SchoolActivity, on_delete=models.CASCADE, related_name='participants'
    )
    teacher = models.ForeignKey(
        Teacher, on_delete=models.CASCADE, related_name='activity_participations'
    )
    role = models.CharField(max_length=50, choices=Role.choices, default=Role.PARTICIPANT)
    attendance_status = models.CharField(
        max_length=50, choices=AttendanceStatus.choices, default=AttendanceStatus.REGISTERED
    )
    certificate_issued = models.BooleanField(default=False)
    notes = models.CharField(max_length=255, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'activity_participant'
        unique_together = ('activity', 'teacher')
        ordering = ['teacher__user__last_name', 'teacher__user__first_name']
        verbose_name = 'Activity Participant'
        verbose_name_plural = 'Activity Participants'

    def __str__(self):
        return f'{self.teacher.user.get_full_name()} - {self.activity.title} ({self.attendance_status})'
