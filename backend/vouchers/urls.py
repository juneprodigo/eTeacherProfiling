from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VoucherTransactionViewSet

router = DefaultRouter()
router.register(r'transactions', VoucherTransactionViewSet, basename='voucher-transaction')

urlpatterns = [
    path('', include(router.urls)),
]
