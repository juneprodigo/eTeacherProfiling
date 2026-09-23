"""
pds/urls.py — PDS URL Patterns for all CS Form 212 sections
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TeacherViewSet,
    PersonalInfoView, FamilyBackgroundView,
    EducationalBackgroundListView, EducationalBackgroundDetailView,
    CivilServiceEligibilityListView, CivilServiceEligibilityDetailView,
    WorkExperienceListView, WorkExperienceDetailView,
    LearningDevelopmentListView, LearningDevelopmentDetailView,
    VoluntaryWorkListView, VoluntaryWorkDetailView,
    OtherInformationView, GovernmentQuestionsView,
    ReferenceListView, ReferenceDetailView,
    PDSDeclarationView,
)
from .analytics_views import (
    TeacherDemographicsAnalyticsView,
    TrainingMonitoringHubView,
)

router = DefaultRouter()
router.register(r'teachers', TeacherViewSet, basename='teacher')

urlpatterns = [
    path('', include(router.urls)),

    # Analytics & Training Hub
    path('analytics/demographics/', TeacherDemographicsAnalyticsView.as_view(), name='analytics-demographics'),
    path('analytics/trainings/', TrainingMonitoringHubView.as_view(), name='analytics-trainings'),

    # Section I — Personal Information
    path('teachers/<int:teacher_pk>/personal-info/', PersonalInfoView.as_view(), name='personal-info'),

    # Section II — Family Background
    path('teachers/<int:teacher_pk>/family-background/', FamilyBackgroundView.as_view(), name='family-background'),

    # Section III — Educational Background
    path('teachers/<int:teacher_pk>/educational-background/', EducationalBackgroundListView.as_view(), name='educational-background-list'),
    path('teachers/<int:teacher_pk>/educational-background/<int:pk>/', EducationalBackgroundDetailView.as_view(), name='educational-background-detail'),

    # Section IV — Civil Service Eligibility
    path('teachers/<int:teacher_pk>/civil-service-eligibility/', CivilServiceEligibilityListView.as_view(), name='cse-list'),
    path('teachers/<int:teacher_pk>/civil-service-eligibility/<int:pk>/', CivilServiceEligibilityDetailView.as_view(), name='cse-detail'),

    # Section V — Work Experience
    path('teachers/<int:teacher_pk>/work-experience/', WorkExperienceListView.as_view(), name='work-experience-list'),
    path('teachers/<int:teacher_pk>/work-experience/<int:pk>/', WorkExperienceDetailView.as_view(), name='work-experience-detail'),

    # Section VI — Learning & Development
    path('teachers/<int:teacher_pk>/learning-development/', LearningDevelopmentListView.as_view(), name='ld-list'),
    path('teachers/<int:teacher_pk>/learning-development/<int:pk>/', LearningDevelopmentDetailView.as_view(), name='ld-detail'),

    # Section VII — Voluntary Work
    path('teachers/<int:teacher_pk>/voluntary-work/', VoluntaryWorkListView.as_view(), name='voluntary-work-list'),
    path('teachers/<int:teacher_pk>/voluntary-work/<int:pk>/', VoluntaryWorkDetailView.as_view(), name='voluntary-work-detail'),

    # Section VIII — Other Information
    path('teachers/<int:teacher_pk>/other-information/', OtherInformationView.as_view(), name='other-information'),

    # Government Questions (Items 34–40)
    path('teachers/<int:teacher_pk>/government-questions/', GovernmentQuestionsView.as_view(), name='government-questions'),

    # References (Item 41)
    path('teachers/<int:teacher_pk>/references/', ReferenceListView.as_view(), name='reference-list'),
    path('teachers/<int:teacher_pk>/references/<int:pk>/', ReferenceDetailView.as_view(), name='reference-detail'),

    # Declaration (Item 42)
    path('teachers/<int:teacher_pk>/declaration/', PDSDeclarationView.as_view(), name='pds-declaration'),
]
