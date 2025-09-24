from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import uuid

class CustomUser(AbstractUser):
    """
    Extended User model for BulamuChainBot
    """
    USER_TYPES = [
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
        ('nurse', 'Nurse'),
        ('admin', 'Administrator'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='patient')
    phone_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    verification_code = models.CharField(max_length=6, blank=True)
    
    # Profile completion
    profile_completed = models.BooleanField(default=False)
    terms_accepted = models.BooleanField(default=False)
    privacy_consent = models.BooleanField(default=False)
    
    # Timestamps
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.username} ({self.user_type})"

class UserProfile(models.Model):
    """
    Additional profile information for users
    """
    LANGUAGES = [
        ('en', 'English'),
        ('lg', 'Luganda'),
    ]
    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    
    # Personal information
    bio = models.TextField(blank=True, max_length=500)
    avatar = models.ImageField(upload_to='profiles/avatars/', blank=True, null=True)
    preferred_language = models.CharField(max_length=2, choices=LANGUAGES, default='en')
    
    # Notifications preferences
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    emergency_notifications = models.BooleanField(default=True)
    
    # Privacy settings
    profile_visibility = models.BooleanField(default=True)
    data_sharing_consent = models.BooleanField(default=False)
    
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Profile of {self.user.username}"

class DoctorProfile(models.Model):
    """
    Extended profile for healthcare providers
    """
    SPECIALIZATIONS = [
        ('general', 'General Practice'),
        ('pediatrics', 'Pediatrics'),
        ('internal', 'Internal Medicine'),
        ('obstetrics', 'Obstetrics & Gynecology'),
        ('surgery', 'Surgery'),
        ('psychiatry', 'Psychiatry'),
        ('dermatology', 'Dermatology'),
        ('ophthalmology', 'Ophthalmology'),
        ('emergency', 'Emergency Medicine'),
        ('other', 'Other'),
    ]
    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='doctor_profile')
    
    # Professional information
    license_number = models.CharField(max_length=100, unique=True)
    specialization = models.CharField(max_length=20, choices=SPECIALIZATIONS, default='general')
    years_of_experience = models.PositiveIntegerField(default=0)
    
    # Institution
    hospital_name = models.CharField(max_length=200, blank=True)
    hospital_address = models.TextField(blank=True)
    department = models.CharField(max_length=100, blank=True)
    
    # Verification
    is_verified = models.BooleanField(default=False)
    verification_document = models.FileField(upload_to='doctors/verification/', blank=True, null=True)
    verified_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_doctors')
    verified_at = models.DateTimeField(null=True, blank=True)
    
    # Availability
    is_available = models.BooleanField(default=True)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Dr. {self.user.get_full_name() or self.user.username}"

class LoginAttempt(models.Model):
    """
    Track login attempts for security
    """
    ATTEMPT_TYPES = [
        ('success', 'Successful Login'),
        ('failed_password', 'Failed - Wrong Password'),
        ('failed_username', 'Failed - Wrong Username'),
        ('blocked', 'Blocked - Too Many Attempts'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=150)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    attempt_type = models.CharField(max_length=20, choices=ATTEMPT_TYPES)
    
    # Geolocation (optional)
    country = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    
    timestamp = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['username', 'timestamp']),
            models.Index(fields=['ip_address', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.attempt_type} - {self.username} from {self.ip_address}"

class OTPVerification(models.Model):
    """
    One-time passwords for phone verification and password reset
    """
    OTP_TYPES = [
        ('phone_verification', 'Phone Verification'),
        ('password_reset', 'Password Reset'),
        ('two_factor', 'Two-Factor Authentication'),
        ('emergency_access', 'Emergency Access'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='otp_codes')
    otp_type = models.CharField(max_length=20, choices=OTP_TYPES)
    phone_number = models.CharField(max_length=20)
    
    code = models.CharField(max_length=6)
    is_used = models.BooleanField(default=False)
    attempts = models.PositiveIntegerField(default=0)
    max_attempts = models.PositiveIntegerField(default=3)
    
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def is_valid(self):
        return not self.is_used and self.attempts < self.max_attempts and timezone.now() < self.expires_at
    
    def __str__(self):
        return f"OTP {self.code} for {self.user.username} ({self.otp_type})"
