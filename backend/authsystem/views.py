from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model, authenticate
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta
import random
import string

from .models import CustomUser, UserProfile, DoctorProfile, LoginAttempt, OTPVerification
from .serializers import (
    UserRegistrationSerializer, UserProfileSerializer, 
    DoctorProfileSerializer, DoctorRegistrationSerializer,
    OTPRequestSerializer, OTPVerificationSerializer,
    PasswordResetSerializer, PasswordResetConfirmSerializer,
    UserSummarySerializer
)
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class RegisterView(APIView):
    """
    User registration endpoint
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            
            # Create user profile
            UserProfile.objects.create(user=user)
            
            # Send OTP for phone verification if phone number provided
            phone_number = serializer.validated_data.get('phone_number')
            if phone_number:
                self._send_verification_otp(user, phone_number)
            
            return Response({
                'message': 'User registered successfully',
                'user_id': str(user.id),
                'username': user.username,
                'requires_phone_verification': bool(phone_number)
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def _send_verification_otp(self, user, phone_number):
        """Send OTP for phone verification"""
        # Generate OTP
        otp_code = ''.join(random.choices(string.digits, k=6))
        
        # Create OTP record
        OTPVerification.objects.create(
            user=user,
            otp_type='phone_verification',
            phone_number=phone_number,
            code=otp_code,
            expires_at=timezone.now() + timedelta(minutes=10)
        )
        
        # TODO: Send SMS with OTP
        # For development, just log it
        print(f"OTP for {phone_number}: {otp_code}")

class LoginView(APIView):
    """
    Custom login endpoint that accepts email or username
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        username_or_email = request.data.get('username', '')
        password = request.data.get('password', '')
        
        if not username_or_email or not password:
            return Response({
                'error': 'Username/email and password are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Try to find user by email first, then by username
        user = None
        if '@' in username_or_email:
            try:
                user = CustomUser.objects.get(email=username_or_email)
                username = user.username
            except CustomUser.DoesNotExist:
                pass
        else:
            username = username_or_email
        
        # Authenticate user
        authenticated_user = authenticate(request, username=username, password=password)
        
        if authenticated_user:
            # Generate JWT tokens
            refresh = RefreshToken.for_user(authenticated_user)
            
            # Log successful login
            LoginAttempt.objects.create(
                user=authenticated_user,
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT'),
                attempt_type='success'
            )
            
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': {
                    'id': str(authenticated_user.id),
                    'username': authenticated_user.username,
                    'email': authenticated_user.email,
                    'first_name': authenticated_user.first_name,
                    'last_name': authenticated_user.last_name,
                    'user_type': authenticated_user.user_type,
                }
            }, status=status.HTTP_200_OK)
        else:
            # Log failed login
            try:
                user_for_log = CustomUser.objects.get(
                    username=username if '@' not in username_or_email else username_or_email
                ) if '@' not in username_or_email else CustomUser.objects.get(email=username_or_email)
                
                LoginAttempt.objects.create(
                    user=user_for_log,
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT'),
                    attempt_type='failed_password'
                )
            except CustomUser.DoesNotExist:
                # User doesn't exist, log as failed username
                pass
            
            return Response({
                'error': 'Invalid credentials'
            }, status=status.HTTP_400_BAD_REQUEST)

class VerifyPhoneView(APIView):
    """
    Phone number verification endpoint
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = OTPVerificationSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        otp_code = serializer.validated_data['otp_code']
        
        try:
            otp = OTPVerification.objects.get(
                user=request.user,
                code=otp_code,
                otp_type='phone_verification',
                is_used=False
            )
            
            if not otp.is_valid():
                otp.attempts += 1
                otp.save()
                
                if otp.attempts >= otp.max_attempts:
                    return Response({
                        'error': 'Maximum verification attempts exceeded'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                return Response({
                    'error': 'Invalid or expired OTP'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Mark OTP as used
            otp.is_used = True
            otp.used_at = timezone.now()
            otp.save()
            
            # Mark user as verified
            user = request.user
            user.is_verified = True
            user.save()
            
            return Response({
                'message': 'Phone number verified successfully'
            })
            
        except OTPVerification.DoesNotExist:
            return Response({
                'error': 'Invalid OTP code'
            }, status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    User profile management
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile

class DoctorRegisterView(APIView):
    """
    Doctor registration endpoint
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = DoctorRegistrationSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            
            # Create user profile
            UserProfile.objects.create(user=user)
            
            return Response({
                'message': 'Doctor registered successfully. Awaiting verification.',
                'user_id': str(user.id),
                'username': user.username
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DoctorProfileView(generics.RetrieveUpdateAPIView):
    """
    Doctor profile management
    """
    serializer_class = DoctorProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        if self.request.user.user_type != 'doctor':
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only doctors can access doctor profiles")
        
        profile, created = DoctorProfile.objects.get_or_create(user=self.request.user)
        return profile

class RequestOTPView(APIView):
    """
    Request OTP for various purposes
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = OTPRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        otp_type = serializer.validated_data['otp_type']
        phone_number = serializer.validated_data['phone_number']
        
        # Generate OTP
        otp_code = ''.join(random.choices(string.digits, k=6))
        
        # Create OTP record
        OTPVerification.objects.create(
            user=request.user,
            otp_type=otp_type,
            phone_number=phone_number,
            code=otp_code,
            expires_at=timezone.now() + timedelta(minutes=10)
        )
        
        # TODO: Send SMS
        print(f"OTP for {phone_number}: {otp_code}")
        
        return Response({
            'message': f'OTP sent to {phone_number}',
            'expires_in': 600  # 10 minutes
        })

class VerifyOTPView(APIView):
    """
    Verify OTP for various purposes
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = OTPVerificationSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        otp_code = serializer.validated_data['otp_code']
        otp_type = serializer.validated_data.get('otp_type', 'phone_verification')
        
        try:
            otp = OTPVerification.objects.get(
                user=request.user,
                code=otp_code,
                otp_type=otp_type,
                is_used=False
            )
            
            if not otp.is_valid():
                otp.attempts += 1
                otp.save()
                
                return Response({
                    'error': 'Invalid or expired OTP'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Mark OTP as used
            otp.is_used = True
            otp.used_at = timezone.now()
            otp.save()
            
            return Response({
                'message': 'OTP verified successfully',
                'otp_type': otp_type
            })
            
        except OTPVerification.DoesNotExist:
            return Response({
                'error': 'Invalid OTP code'
            }, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetView(APIView):
    """
    Request password reset
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        username_or_phone = serializer.validated_data['username_or_phone']
        
        # Find user by username or phone
        try:
            user = User.objects.get(username=username_or_phone)
        except User.DoesNotExist:
            try:
                user = User.objects.get(phone_number=username_or_phone)
            except User.DoesNotExist:
                # Don't reveal if user exists or not
                return Response({
                    'message': 'If the account exists, a reset code will be sent'
                })
        
        if user.phone_number:
            # Generate OTP for password reset
            otp_code = ''.join(random.choices(string.digits, k=6))
            
            OTPVerification.objects.create(
                user=user,
                otp_type='password_reset',
                phone_number=user.phone_number,
                code=otp_code,
                expires_at=timezone.now() + timedelta(minutes=15)
            )
            
            # TODO: Send SMS
            print(f"Password reset OTP for {user.phone_number}: {otp_code}")
            
            return Response({
                'message': 'Reset code sent to your phone number'
            })
        
        return Response({
            'message': 'If the account exists, a reset code will be sent'
        })

class PasswordResetConfirmView(APIView):
    """
    Confirm password reset with OTP
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        otp_code = serializer.validated_data['otp_code']
        new_password = serializer.validated_data['new_password']
        
        try:
            otp = OTPVerification.objects.get(
                code=otp_code,
                otp_type='password_reset',
                is_used=False
            )
            
            if not otp.is_valid():
                return Response({
                    'error': 'Invalid or expired reset code'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Update password
            user = otp.user
            user.set_password(new_password)
            user.save()
            
            # Mark OTP as used
            otp.is_used = True
            otp.used_at = timezone.now()
            otp.save()
            
            return Response({
                'message': 'Password reset successfully'
            })
            
        except OTPVerification.DoesNotExist:
            return Response({
                'error': 'Invalid reset code'
            }, status=status.HTTP_400_BAD_REQUEST)


class CurrentUserView(generics.RetrieveAPIView):
    """
    Get current authenticated user information
    """
    serializer_class = UserSummarySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
