from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser, UserProfile, DoctorProfile, OTPVerification

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration
    """
    password = serializers.CharField(
        write_only=True, 
        validators=[validate_password],
        help_text="Password must be at least 8 characters long"
    )
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = CustomUser
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'phone_number', 'user_type'
        ]
        extra_kwargs = {
            'email': {'required': True}
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        
        # Remove password_confirm from validated data
        attrs.pop('password_confirm')
        return attrs
    
    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already registered")
        return value
    
    def validate_username(self, value):
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already taken")
        return value
    
    def validate_phone_number(self, value):
        if value and CustomUser.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("Phone number already registered")
        return value
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = CustomUser.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user

class DoctorRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for doctor registration
    """
    password = serializers.CharField(
        write_only=True, 
        validators=[validate_password]
    )
    password_confirm = serializers.CharField(write_only=True)
    license_number = serializers.CharField()
    specialization = serializers.CharField()
    hospital_name = serializers.CharField(required=False)
    
    class Meta:
        model = CustomUser
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'phone_number',
            'license_number', 'specialization', 'hospital_name'
        ]
        extra_kwargs = {
            'email': {'required': True}
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        
        attrs.pop('password_confirm')
        return attrs
    
    def validate_license_number(self, value):
        if DoctorProfile.objects.filter(license_number=value).exists():
            raise serializers.ValidationError("License number already registered")
        return value
    
    def create(self, validated_data):
        # Extract doctor-specific fields
        license_number = validated_data.pop('license_number')
        specialization = validated_data.pop('specialization')
        hospital_name = validated_data.pop('hospital_name', '')
        
        # Create user
        password = validated_data.pop('password')
        validated_data['user_type'] = 'doctor'
        user = CustomUser.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        
        # Create doctor profile
        DoctorProfile.objects.create(
            user=user,
            license_number=license_number,
            specialization=specialization,
            hospital_name=hospital_name
        )
        
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile
    """
    user_info = serializers.SerializerMethodField()
    
    class Meta:
        model = UserProfile
        fields = [
            'bio', 'avatar', 'preferred_language', 'email_notifications',
            'sms_notifications', 'emergency_notifications',
            'profile_visibility', 'data_sharing_consent', 'user_info'
        ]
    
    def get_user_info(self, obj):
        return {
            'username': obj.user.username,
            'email': obj.user.email,
            'full_name': obj.user.get_full_name(),
            'user_type': obj.user.user_type,
            'is_verified': obj.user.is_verified,
            'phone_number': obj.user.phone_number
        }

class DoctorProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for doctor profile
    """
    user_info = serializers.SerializerMethodField()
    specialization_display = serializers.CharField(source='get_specialization_display', read_only=True)
    
    class Meta:
        model = DoctorProfile
        fields = [
            'license_number', 'specialization', 'specialization_display',
            'years_of_experience', 'hospital_name', 'hospital_address',
            'department', 'is_verified', 'is_available',
            'consultation_fee', 'user_info'
        ]
        read_only_fields = ['license_number', 'is_verified']
    
    def get_user_info(self, obj):
        return {
            'username': obj.user.username,
            'email': obj.user.email,
            'full_name': obj.user.get_full_name(),
            'phone_number': obj.user.phone_number
        }

class OTPRequestSerializer(serializers.Serializer):
    """
    Serializer for OTP requests
    """
    otp_type = serializers.ChoiceField(
        choices=['phone_verification', 'password_reset', 'two_factor', 'emergency_access']
    )
    phone_number = serializers.CharField(max_length=20)
    
    def validate_phone_number(self, value):
        # Basic phone number validation
        import re
        if not re.match(r'^\+?[1-9]\d{1,14}$', value.replace(' ', '')):
            raise serializers.ValidationError("Invalid phone number format")
        return value

class OTPVerificationSerializer(serializers.Serializer):
    """
    Serializer for OTP verification
    """
    otp_code = serializers.CharField(max_length=6, min_length=6)
    otp_type = serializers.ChoiceField(
        choices=['phone_verification', 'password_reset', 'two_factor', 'emergency_access'],
        required=False
    )
    
    def validate_otp_code(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("OTP must contain only digits")
        return value

class PasswordResetSerializer(serializers.Serializer):
    """
    Serializer for password reset requests
    """
    username_or_phone = serializers.CharField(
        help_text="Enter your username or phone number"
    )

class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Serializer for password reset confirmation
    """
    otp_code = serializers.CharField(max_length=6, min_length=6)
    new_password = serializers.CharField(validators=[validate_password])
    new_password_confirm = serializers.CharField()
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        
        attrs.pop('new_password_confirm')
        return attrs
    
    def validate_otp_code(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("OTP must contain only digits")
        return value

class LoginAttemptSerializer(serializers.Serializer):
    """
    Serializer for login attempts logging
    """
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        if not username or not password:
            raise serializers.ValidationError("Username and password required")
        
        return attrs

class UserSummarySerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for user information
    """
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    user_type_display = serializers.CharField(source='get_user_type_display', read_only=True)
    
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name', 'user_type',
            'user_type_display', 'is_verified', 'date_joined'
        ]
