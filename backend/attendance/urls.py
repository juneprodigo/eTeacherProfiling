from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DailyTimeRecordViewSet, LeaveApplicationViewSet, LeaveBalanceViewSet

router = DefaultRouter()
router.register('records', DailyTimeRecordViewSet, basename='attendance-records')
router.register('leaves', LeaveApplicationViewSet, basename='attendance-leaves')
router.register('balances', LeaveBalanceViewSet, basename='attendance-balances')

urlpatterns = [
    path('', include(router.urls)),
]
