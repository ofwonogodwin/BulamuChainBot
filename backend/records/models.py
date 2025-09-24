from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid
import hashlib

User = get_user_model()

class MedicalRecord(models.Model):
    """
    Model to store medical records with blockchain hash references
    """
    RECORD_TYPES = [
        ('consultation', 'Consultation Record'),
        ('prescription', 'Prescription'),
        ('test_result', 'Test Result'),
        ('vaccine', 'Vaccination Record'),
        ('allergy', 'Allergy Information'),
        ('emergency', 'Emergency Treatment'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='medical_records')
    record_type = models.CharField(max_length=20, choices=RECORD_TYPES)
    
    # Medical data
    title = models.CharField(max_length=200)
    description = models.TextField()
    diagnosis = models.TextField(blank=True)
    treatment = models.TextField(blank=True)
    medications = models.TextField(blank=True)
    
    # File attachments
    document_file = models.FileField(upload_to='records/documents/', blank=True, null=True)
    image_file = models.FileField(upload_to='records/images/', blank=True, null=True)
    
    # Blockchain integration
    record_hash = models.CharField(max_length=64, unique=True, editable=False)
    blockchain_tx_hash = models.CharField(max_length=66, blank=True, null=True)
    is_on_blockchain = models.BooleanField(default=False)
    
    # Healthcare provider info
    provider_name = models.CharField(max_length=200, blank=True)
    provider_license = models.CharField(max_length=100, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_emergency = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['patient', 'record_type']),
            models.Index(fields=['record_hash']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.record_hash:
            # Generate hash of the medical record content
            content = f"{self.patient.id}{self.title}{self.description}{self.created_at}"
            self.record_hash = hashlib.sha256(content.encode()).hexdigest()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.record_type}: {self.title} - {self.patient.username}"

class PatientProfile(models.Model):
    """
    Extended patient profile with medical history
    """
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
        ('P', 'Prefer not to say'),
    ]
    
    BLOOD_TYPES = [
        ('A+', 'A Positive'),
        ('A-', 'A Negative'),
        ('B+', 'B Positive'),
        ('B-', 'B Negative'),
        ('AB+', 'AB Positive'),
        ('AB-', 'AB Negative'),
        ('O+', 'O Positive'),
        ('O-', 'O Negative'),
        ('Unknown', 'Unknown'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')
    
    # Basic info
    phone_number = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    blood_type = models.CharField(max_length=10, choices=BLOOD_TYPES, default='Unknown')
    
    # Address
    address = models.TextField(blank=True)
    village = models.CharField(max_length=100, blank=True)
    parish = models.CharField(max_length=100, blank=True)
    subcounty = models.CharField(max_length=100, blank=True)
    district = models.CharField(max_length=100, blank=True)
    
    # Medical history
    allergies = models.TextField(blank=True, help_text="Known allergies separated by commas")
    chronic_conditions = models.TextField(blank=True, help_text="Chronic medical conditions")
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    
    # Language preferences
    preferred_language = models.CharField(max_length=2, choices=[('en', 'English'), ('lg', 'Luganda')], default='en')
    
    # Blockchain
    profile_hash = models.CharField(max_length=64, unique=True, editable=False, blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.profile_hash:
            content = f"{self.user.id}{self.phone_number}{self.date_of_birth}"
            self.profile_hash = hashlib.sha256(content.encode()).hexdigest()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Patient Profile: {self.user.get_full_name() or self.user.username}"

class RecordAccessLog(models.Model):
    """
    Log access to medical records for audit purposes
    """
    ACCESS_TYPES = [
        ('view', 'View Record'),
        ('create', 'Create Record'),
        ('update', 'Update Record'),
        ('delete', 'Delete Record'),
        ('blockchain_store', 'Store on Blockchain'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    medical_record = models.ForeignKey(MedicalRecord, on_delete=models.CASCADE, related_name='access_logs')
    accessed_by = models.ForeignKey(User, on_delete=models.CASCADE)
    access_type = models.CharField(max_length=20, choices=ACCESS_TYPES)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.access_type} by {self.accessed_by.username} at {self.timestamp}"
