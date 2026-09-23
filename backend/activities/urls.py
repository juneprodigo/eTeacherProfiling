from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SchoolActivityViewSet

router = DefaultRouter()
router.register(r'', SchoolActivityViewSet, basename='school-activities')

urlpatterns = [
    path('', include(router.urls)),
]
