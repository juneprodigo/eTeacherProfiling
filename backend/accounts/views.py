"""
accounts/views.py — Authentication and User Management Views
"""
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

from .serializers import (
    CustomTokenObtainPairSerializer,
    UserListSerializer,
    UserDetailSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
    ChangePasswordSerializer,
)
from .permissions import IsAdmin, IsHROrAdmin, IsOwnerOrHROrAdmin

User = get_user_model()


class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = CustomTokenObtainPairSerializer


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Successfully logged out.'}, status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response({'error': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserDetailSerializer(request.user, context={'request': request})
        return Response(serializer.data)

    def patch(self, request):
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserDetailSerializer(request.user, context={'request': request}).data)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        if not user.check_password(serializer.validated_data['old_password']):
            return Response({'error': 'Current password is incorrect.'}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({'message': 'Password updated successfully.'})


class UserListCreateView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    permission_classes = [IsHROrAdmin]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserCreateSerializer
        return UserListSerializer

    def get_queryset(self):
        qs = User.objects.all()
        role = self.request.query_params.get('role')
        search = self.request.query_params.get('search')
        if role:
            qs = qs.filter(role=role)
        if search:
            qs = qs.filter(
                username__icontains=search
            ) | qs.filter(
                first_name__icontains=search
            ) | qs.filter(
                last_name__icontains=search
            ) | qs.filter(
                email__icontains=search
            )
        return qs.order_by('last_name', 'first_name')


class UserDetailUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    permission_classes = [IsOwnerOrHROrAdmin]

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return UserUpdateSerializer
        return UserDetailSerializer

    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [IsAdmin()]
        return super().get_permissions()

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        if user == request.user:
            return Response(
                {'error': 'You cannot delete your own account.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        user.is_active = False
        user.save()
        return Response({'message': 'User deactivated successfully.'}, status=status.HTTP_200_OK)


class DashboardStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from pds.models import Teacher
        total_teachers = Teacher.objects.filter(user__is_active=True).count()
        total_users = User.objects.filter(is_active=True).count()
        active_hr = User.objects.filter(role='hr', is_active=True).count()

        # PDS completion stats
        complete_pds = Teacher.objects.filter(pds_complete=True).count()

        return Response({
            'total_teachers': total_teachers,
            'total_users': total_users,
            'active_hr_officers': active_hr,
            'complete_pds': complete_pds,
            'incomplete_pds': total_teachers - complete_pds,
            'user_role': request.user.role,
        })
