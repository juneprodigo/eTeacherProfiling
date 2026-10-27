from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    StepIncrementRecordViewSet,
    StepIncrementDocumentViewSet,
    NosiAlertViewSet,
    TeacherNosiEligibilityView,
    StepIncrementSalaryScheduleViewSet,
    ServiceRecordEntryViewSet,
    SalaryAdjustmentRecordViewSet,
    AppointmentRecordViewSet
)

router = DefaultRouter()
router.register(r'records', StepIncrementRecordViewSet, basename='nosi-records')
router.register(r'documents', StepIncrementDocumentViewSet, basename='nosi-documents')
router.register(r'alerts', NosiAlertViewSet, basename='nosi-alerts')
router.register(r'salary-schedules', StepIncrementSalaryScheduleViewSet, basename='nosi-salary-schedules')
router.register(r'service-records', ServiceRecordEntryViewSet, basename='nosi-service-records')
router.register(r'nosa', SalaryAdjustmentRecordViewSet, basename='nosi-nosa')
router.register(r'appointments', AppointmentRecordViewSet, basename='nosi-appointments')

urlpatterns = [
    path('eligibility/', TeacherNosiEligibilityView.as_view(), name='nosi-eligibility'),
    path('', include(router.urls)),
]

