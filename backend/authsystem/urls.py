from django.urls import path
from . import views

urlpatterns = [
    # User registration and authentication
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('verify-phone/', views.VerifyPhoneView.as_view(), name='verify-phone'),
    path('profile/', views.UserProfileView.as_view(), name='user-profile'),
    
    # Doctor-specific endpoints
    path('doctors/register/', views.DoctorRegisterView.as_view(), name='doctor-register'),
    path('doctors/profile/', views.DoctorProfileView.as_view(), name='doctor-profile'),
    
    # Password reset
    path('password/reset/', views.PasswordResetView.as_view(), name='password-reset'),
    path('password/reset/confirm/', views.PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    
    # OTP management
    path('otp/request/', views.RequestOTPView.as_view(), name='request-otp'),
    path('otp/verify/', views.VerifyOTPView.as_view(), name='verify-otp'),
]
