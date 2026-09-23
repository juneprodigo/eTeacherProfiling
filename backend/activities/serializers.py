from rest_framework import serializers
from .models import SchoolActivity, ActivityParticipant
from pds.serializers import TeacherListSerializer
from pds.models import Teacher


class ActivityParticipantSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.user.get_full_name', read_only=True)
    teacher_department = serializers.CharField(source='teacher.department', read_only=True)
    teacher_position = serializers.CharField(source='teacher.position', read_only=True)
    teacher_email = serializers.CharField(source='teacher.user.email', read_only=True)

    class Meta:
        model = ActivityParticipant
        fields = [
            'id', 'activity', 'teacher', 'teacher_name', 'teacher_department',
            'teacher_position', 'teacher_email', 'role', 'attendance_status',
            'certificate_issued', 'notes', 'created_at'
        ]


class SchoolActivitySerializer(serializers.ModelSerializer):
    coordinator_name = serializers.SerializerMethodField()
    participant_count = serializers.IntegerField(read_only=True)
    attended_count = serializers.IntegerField(read_only=True)
    participants = ActivityParticipantSerializer(many=True, read_only=True)
    attachment_url = serializers.SerializerMethodField()

    class Meta:
        model = SchoolActivity
        fields = [
            'id', 'title', 'activity_type', 'description', 'venue', 'modality',
            'start_date', 'end_date', 'status', 'coordinator', 'coordinator_name',
            'budget', 'funding_source', 'attachment', 'attachment_url',
            'participant_count', 'attended_count', 'participants',
            'created_at', 'updated_at'
        ]

    def get_coordinator_name(self, obj):
        if obj.coordinator:
            return obj.coordinator.user.get_full_name()
        return None

    def get_attachment_url(self, obj):
        request = self.context.get('request')
        if obj.attachment and request:
            return request.build_absolute_uri(obj.attachment.url)
        elif obj.attachment:
            return obj.attachment.url
        return None
