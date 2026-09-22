"""
pds/admin.py — Admin Registration for all PDS Models
"""
from django.contrib import admin
from .models import (
    Teacher, PersonalInfo, FamilyBackground, ChildInfo,
    EducationalBackground, CivilServiceEligibility, WorkExperience,
    LearningDevelopment, VoluntaryWork, OtherInformation,
    GovernmentQuestions, Reference, PDSDeclaration,
)


class PersonalInfoInline(admin.StackedInline):
    model = PersonalInfo
    can_delete = False
    extra = 0


class FamilyBackgroundInline(admin.StackedInline):
    model = FamilyBackground
    can_delete = False
    extra = 0


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['get_full_name', 'employee_id', 'department', 'position', 'pds_complete', 'created_at']
    list_filter = ['pds_complete', 'department']
    search_fields = ['user__first_name', 'user__last_name', 'employee_id', 'department']
    inlines = [PersonalInfoInline, FamilyBackgroundInline]

    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = 'Full Name'
    get_full_name.admin_order_field = 'user__last_name'


@admin.register(EducationalBackground)
class EducationalBackgroundAdmin(admin.ModelAdmin):
    list_display = ['teacher', 'level', 'school_name', 'degree_course', 'year_graduated']
    list_filter = ['level']
    search_fields = ['teacher__user__last_name', 'school_name', 'degree_course']


@admin.register(CivilServiceEligibility)
class CivilServiceEligibilityAdmin(admin.ModelAdmin):
    list_display = ['teacher', 'eligibility_type', 'rating', 'examination_date', 'license_number']
    search_fields = ['teacher__user__last_name', 'eligibility_type']


@admin.register(WorkExperience)
class WorkExperienceAdmin(admin.ModelAdmin):
    list_display = ['teacher', 'position_title', 'department_agency_company', 'from_date', 'to_date']
    search_fields = ['teacher__user__last_name', 'position_title', 'department_agency_company']


@admin.register(LearningDevelopment)
class LearningDevelopmentAdmin(admin.ModelAdmin):
    list_display = ['teacher', 'training_title', 'from_date', 'to_date', 'number_of_hours', 'ld_type']
    list_filter = ['ld_type']
    search_fields = ['teacher__user__last_name', 'training_title']


@admin.register(VoluntaryWork)
class VoluntaryWorkAdmin(admin.ModelAdmin):
    list_display = ['teacher', 'organization_name_address', 'from_date', 'to_date', 'number_of_hours']
    search_fields = ['teacher__user__last_name', 'organization_name_address']


admin.site.register(PersonalInfo)
admin.site.register(FamilyBackground)
admin.site.register(ChildInfo)
admin.site.register(OtherInformation)
admin.site.register(GovernmentQuestions)
admin.site.register(Reference)
admin.site.register(PDSDeclaration)
