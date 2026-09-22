"""
pds/serializers.py — CS Form 212 Serializers (all sections)
"""
from rest_framework import serializers
from .models import (
    Teacher, PersonalInfo, FamilyBackground, ChildInfo,
    EducationalBackground, CivilServiceEligibility, WorkExperience,
    LearningDevelopment, VoluntaryWork, OtherInformation,
    GovernmentQuestions, Reference, PDSDeclaration,
)
from accounts.serializers import UserListSerializer


# ── Teacher ───────────────────────────────────────────────────────────────────

class TeacherListSerializer(serializers.ModelSerializer):
    user = UserListSerializer(read_only=True)
    full_name = serializers.SerializerMethodField()
    photo_url = serializers.SerializerMethodField()

    class Meta:
        model = Teacher
        fields = ['id', 'user', 'full_name', 'employee_id', 'department', 'position', 'pds_complete', 'photo_url', 'created_at']

    def get_full_name(self, obj):
        return obj.user.get_full_name()

    def get_photo_url(self, obj):
        request = self.context.get('request')
        if obj.photo and request:
            return request.build_absolute_uri(obj.photo.url)
        if obj.user.profile_photo and request:
            return request.build_absolute_uri(obj.user.profile_photo.url)
        return None


class TeacherCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = ['employee_id', 'department', 'position', 'photo']


class TeacherUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = ['employee_id', 'department', 'position', 'photo']


# ── Section I: Personal Information ──────────────────────────────────────────

class PersonalInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonalInfo
        exclude = ['teacher']


# ── Section II: Family Background ────────────────────────────────────────────

class ChildInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChildInfo
        exclude = ['family_background']


class FamilyBackgroundSerializer(serializers.ModelSerializer):
    children = ChildInfoSerializer(many=True, required=False)

    class Meta:
        model = FamilyBackground
        exclude = ['teacher']

    def create(self, validated_data):
        children_data = validated_data.pop('children', [])
        fb = FamilyBackground.objects.create(**validated_data)
        for child in children_data:
            ChildInfo.objects.create(family_background=fb, **child)
        return fb

    def update(self, instance, validated_data):
        children_data = validated_data.pop('children', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if children_data is not None:
            instance.children.all().delete()
            for child in children_data:
                ChildInfo.objects.create(family_background=instance, **child)
        return instance


# ── Section III: Educational Background ──────────────────────────────────────

class EducationalBackgroundSerializer(serializers.ModelSerializer):
    class Meta:
        model = EducationalBackground
        exclude = ['teacher']


# ── Section IV: Civil Service Eligibility ────────────────────────────────────

class CivilServiceEligibilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = CivilServiceEligibility
        exclude = ['teacher']


# ── Section V: Work Experience ────────────────────────────────────────────────

class WorkExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkExperience
        exclude = ['teacher']


# ── Section VI: Learning & Development ───────────────────────────────────────

class LearningDevelopmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = LearningDevelopment
        exclude = ['teacher']


# ── Section VII: Voluntary Work ──────────────────────────────────────────────

class VoluntaryWorkSerializer(serializers.ModelSerializer):
    class Meta:
        model = VoluntaryWork
        exclude = ['teacher']


# ── Section VIII: Other Information ──────────────────────────────────────────

class OtherInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = OtherInformation
        exclude = ['teacher']


# ── Government Questions ──────────────────────────────────────────────────────

class GovernmentQuestionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = GovernmentQuestions
        exclude = ['teacher']


# ── References ───────────────────────────────────────────────────────────────

class ReferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reference
        exclude = ['teacher']


# ── PDS Declaration ───────────────────────────────────────────────────────────

class PDSDeclarationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PDSDeclaration
        exclude = ['teacher']


# ── Full PDS Summary ─────────────────────────────────────────────────────────

class PDSSummarySerializer(serializers.ModelSerializer):
    """Full PDS data for a teacher — read-only summary."""
    user = UserListSerializer(read_only=True)
    personal_info = PersonalInfoSerializer(read_only=True)
    family_background = FamilyBackgroundSerializer(read_only=True)
    educational_backgrounds = EducationalBackgroundSerializer(many=True, read_only=True)
    civil_service_eligibilities = CivilServiceEligibilitySerializer(many=True, read_only=True)
    work_experiences = WorkExperienceSerializer(many=True, read_only=True)
    learning_developments = LearningDevelopmentSerializer(many=True, read_only=True)
    voluntary_works = VoluntaryWorkSerializer(many=True, read_only=True)
    other_information = OtherInformationSerializer(read_only=True)
    government_questions = GovernmentQuestionsSerializer(read_only=True)
    references = ReferenceSerializer(many=True, read_only=True)
    pds_declaration = PDSDeclarationSerializer(read_only=True)
    photo_url = serializers.SerializerMethodField()

    class Meta:
        model = Teacher
        fields = [
            'id', 'user', 'employee_id', 'department', 'position',
            'pds_complete', 'photo_url', 'created_at', 'updated_at',
            'personal_info', 'family_background', 'educational_backgrounds',
            'civil_service_eligibilities', 'work_experiences',
            'learning_developments', 'voluntary_works', 'other_information',
            'government_questions', 'references', 'pds_declaration',
        ]

    def get_photo_url(self, obj):
        request = self.context.get('request')
        if obj.photo and request:
            return request.build_absolute_uri(obj.photo.url)
        if obj.user.profile_photo and request:
            return request.build_absolute_uri(obj.user.profile_photo.url)
        return None
