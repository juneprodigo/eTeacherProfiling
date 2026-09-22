"""
accounts/serializers.py — Auth and User Serializers
"""
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Adds user info to JWT token payload."""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['email'] = user.email
        token['role'] = user.role
        token['full_name'] = user.get_full_name()
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = UserDetailSerializer(self.user).data
        return data


class UserListSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    profile_photo_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'full_name', 'role', 'role_display', 'profile_photo_url',
            'is_active', 'date_joined',
        ]

    def get_full_name(self, obj):
        return obj.get_full_name()

    def get_profile_photo_url(self, obj):
        request = self.context.get('request')
        if obj.profile_photo and request:
            return request.build_absolute_uri(obj.profile_photo.url)
        return None


class UserDetailSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    profile_photo_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'full_name', 'role', 'role_display', 'profile_photo',
            'profile_photo_url', 'is_active', 'date_joined', 'last_login',
        ]
        read_only_fields = ['date_joined', 'last_login']

    def get_full_name(self, obj):
        return obj.get_full_name()

    def get_profile_photo_url(self, obj):
        request = self.context.get('request')
        if obj.profile_photo and request:
            return request.build_absolute_uri(obj.profile_photo.url)
        return None


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, label='Confirm Password')

    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'role', 'password', 'password2', 'is_active',
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('password2'):
            raise serializers.ValidationError({'password': 'Passwords do not match.'})
        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'email', 'first_name', 'last_name', 'role',
            'profile_photo', 'is_active',
        ]


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password2 = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({'new_password': 'Passwords do not match.'})
        return attrs
