from django.contrib.auth import authenticate
from rest_framework import filters, generics, status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework_simplejwt.views import TokenRefreshView

from academic.models import Enrollment
from academic.permissions import is_head

from .models import User
from .serializers import (
    ManagedUserSerializer,
    SessionRefreshSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
    UserRegistrationSerializer,
    check_password,
)


def auth_response(user):
    refresh = RefreshToken.for_user(user)
    return {
        "token": {"refresh": str(refresh), "access": str(refresh.access_token)},
        "user": UserProfileSerializer(user).data,
    }


class UserRegistrationView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    serializer_class = UserRegistrationSerializer
    throttle_scope = "auth"

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(
            auth_response(serializer.save()), status=status.HTTP_201_CREATED
        )


class UserLoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_scope = "auth"

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(
            email=serializer.validated_data["email"].lower(),
            password=serializer.validated_data["password"],
        )
        if not user:
            return Response(
                {"detail": "Email or password is incorrect."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        return Response(auth_response(user))


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    http_method_names = ["get", "patch", "head", "options"]

    def get_object(self):
        return self.request.user


class PasswordChangeView(APIView):
    def post(self, request):
        old = request.data.get("old_password", "")
        new = request.data.get("password", "")
        if not request.user.check_password(old):
            raise ValidationError({"old_password": "Current password is incorrect."})
        if new != request.data.get("password2"):
            raise ValidationError({"password2": "Passwords do not match."})
        check_password(new, request.user)
        request.user.set_password(new)
        request.user.save()
        return Response({"detail": "Password changed. Please sign in again."})


class LogoutView(APIView):
    def post(self, request):
        try:
            token = RefreshToken(request.data.get("refresh", ""))
            if str(token["user_id"]) != str(request.user.pk):
                raise ValidationError("This refresh token belongs to a different user.")
            token.blacklist()
        except TokenError:
            raise ValidationError("Invalid or expired refresh token.")
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = ManagedUserSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "email"]
    ordering = ["name", "id"]
    ordering_fields = ["name", "id", "created_at"]
    http_method_names = ["get", "post", "put", "patch", "head", "options"]

    def get_permissions(self):
        if self.request.method not in ("GET", "HEAD", "OPTIONS") and not is_head(
            self.request.user
        ):
            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied("Only heads can manage users.")
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        queryset = User.objects.all()
        if not is_head(user):
            if user.user_type == "T":
                students = Enrollment.objects.filter(
                    academic_class__subjects__teacher_id=user
                ).values("student")
                queryset = queryset.filter(pk__in=students) | queryset.filter(
                    pk=user.pk
                )
            else:
                queryset = queryset.filter(pk=user.pk)
        role = self.request.query_params.get("user_type")
        if role:
            queryset = queryset.filter(user_type=role)
        active = self.request.query_params.get("is_active")
        if active in ("true", "false"):
            queryset = queryset.filter(is_active=active == "true")
        return queryset.distinct()

    def get_serializer_class(self):
        return (
            ManagedUserSerializer
            if is_head(self.request.user)
            else UserProfileSerializer
        )


class SessionRefreshView(TokenRefreshView):
    serializer_class = SessionRefreshSerializer
    throttle_scope = "auth"
