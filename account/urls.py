from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import SessionRefreshView
from .views import (UserRegistrationView, UserLoginView, UserProfileView, PasswordChangeView,
                    LogoutView, UserViewSet)

router = DefaultRouter()
router.register('users', UserViewSet, basename='user')
urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('userprofile/', UserProfileView.as_view(), name='profile'),
    path('password/', PasswordChangeView.as_view(), name='password-change'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('refresh/', SessionRefreshView.as_view(), name='token-refresh'),
] + router.urls
