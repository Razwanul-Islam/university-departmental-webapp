from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.utils import get_md5_hash_password
from .models import User


def check_password(password, user=None):
    try:
        validate_password(password, user)
    except DjangoValidationError as error:
        raise serializers.ValidationError({'password': error.messages})


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'user_type', 'is_active', 'created_at']
        read_only_fields = ['id', 'email', 'user_type', 'is_active', 'created_at']


class UserRegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'name', 'password', 'password2']
        extra_kwargs = {'password': {'write_only': True}}

    def validate_email(self, value):
        value = value.lower()
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('This email is already registered.')
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password2': 'Passwords do not match.'})
        check_password(attrs['password'], User(email=attrs['email'], name=attrs['name']))
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        return User.objects.create_user(**validated_data)


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class ManagedUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'user_type', 'is_active', 'password', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_email(self, value):
        value = value.lower()
        existing = User.objects.filter(email__iexact=value)
        if self.instance:
            existing = existing.exclude(pk=self.instance.pk)
        if existing.exists():
            raise serializers.ValidationError('This email is already registered.')
        return value

    def validate(self, attrs):
        if not self.instance and not attrs.get('password'):
            raise serializers.ValidationError({'password': 'A password is required.'})
        if attrs.get('password'):
            check_password(attrs['password'], self.instance or User(email=attrs.get('email'), name=attrs.get('name')))
        if self.instance and self.instance.pk == self.context['request'].user.pk:
            if attrs.get('user_type', 'H') != 'H' or not attrs.get('is_active', True):
                raise serializers.ValidationError('You cannot remove your own head access.')
        if self.instance and self.instance.is_admin:
            if attrs.get('user_type', 'H') != 'H' or not attrs.get('is_active', True):
                raise serializers.ValidationError('Manage superuser permissions through Django admin.')
        if self.instance and attrs.get('user_type', self.instance.user_type) != self.instance.user_type:
            from academic.models import subject, Class, Enrollment, result
            if attrs['user_type'] == 'S' and (subject.objects.filter(teacher_id=self.instance).exists() or Class.objects.filter(class_teacher=self.instance).exists()):
                raise serializers.ValidationError('Reassign teaching duties before changing this role.')
            if attrs['user_type'] != 'S' and (Enrollment.objects.filter(student=self.instance).exists() or result.objects.filter(user_id=self.instance).exists()):
                raise serializers.ValidationError('This student has enrollments or results; preserve their student role.')
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for key, value in validated_data.items():
            setattr(instance, key, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


# Check the password fingerprint before accepting a refresh token too.


class SessionRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        token = RefreshToken(attrs['refresh'])
        user = User.objects.filter(pk=token.get('user_id')).first()
        if not user or not user.is_active or token.get('hash_password') != get_md5_hash_password(user.password):
            raise AuthenticationFailed('Your session expired. Please sign in again.')
        return super().validate(attrs)