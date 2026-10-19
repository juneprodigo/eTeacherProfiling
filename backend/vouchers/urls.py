from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VoucherTransactionViewSet, VoucherReferenceLibraryViewSet

router = DefaultRouter()
router.register(r'transactions', VoucherTransactionViewSet, basename='voucher-transaction')
router.register(r'libraries', VoucherReferenceLibraryViewSet, basename='voucher-library')

urlpatterns = [
    path('', include(router.urls)),
]
