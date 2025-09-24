from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import MedicalRecord, PatientProfile, RecordAccessLog

User = get_user_model()

class PatientProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for patient profiles
    """
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    age = serializers.SerializerMethodField()
    
    class Meta:
        model = PatientProfile
        fields = [
            'user', 'user_name', 'phone_number', 'date_of_birth', 'age',
            'gender', 'blood_type', 'address', 'village', 'parish', 
            'subcounty', 'district', 'allergies', 'chronic_conditions',
            'emergency_contact_name', 'emergency_contact_phone', 
            'preferred_language', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'profile_hash', 'created_at', 'updated_at']
    
    def get_age(self, obj):
        if obj.date_of_birth:
            from datetime import date
            today = date.today()
            return today.year - obj.date_of_birth.year - ((today.month, today.day) < (obj.date_of_birth.month, obj.date_of_birth.day))
        return None

class MedicalRecordSerializer(serializers.ModelSerializer):
    """
    Serializer for medical records
    """
    patient_name = serializers.CharField(source='patient.get_full_name', read_only=True)
    record_type_display = serializers.CharField(source='get_record_type_display', read_only=True)
    
    class Meta:
        model = MedicalRecord
        fields = [
            'id', 'patient', 'patient_name', 'record_type', 'record_type_display',
            'title', 'description', 'diagnosis', 'treatment', 'medications',
            'document_file', 'image_file', 'record_hash', 'blockchain_tx_hash',
            'is_on_blockchain', 'provider_name', 'provider_license',
            'created_at', 'updated_at', 'is_active', 'is_emergency'
        ]
        read_only_fields = [
            'id', 'patient', 'record_hash', 'blockchain_tx_hash', 
            'is_on_blockchain', 'created_at', 'updated_at'
        ]

class MedicalRecordCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating medical records
    """
    class Meta:
        model = MedicalRecord
        fields = [
            'record_type', 'title', 'description', 'diagnosis', 
            'treatment', 'medications', 'document_file', 'image_file',
            'provider_name', 'provider_license', 'is_emergency'
        ]
    
    def validate_title(self, value):
        if len(value.strip()) < 5:
            raise serializers.ValidationError(
                "Record title should be at least 5 characters long."
            )
        return value.strip()
    
    def validate_description(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError(
                "Record description should be at least 10 characters long."
            )
        return value.strip()

class MedicalRecordListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing medical records
    """
    record_type_display = serializers.CharField(source='get_record_type_display', read_only=True)
    has_attachments = serializers.SerializerMethodField()
    
    class Meta:
        model = MedicalRecord
        fields = [
            'id', 'record_type', 'record_type_display', 'title', 
            'provider_name', 'is_on_blockchain', 'is_emergency',
            'has_attachments', 'created_at', 'is_active'
        ]
    
    def get_has_attachments(self, obj):
        return bool(obj.document_file or obj.image_file)

class RecordAccessLogSerializer(serializers.ModelSerializer):
    """
    Serializer for record access logs
    """
    accessed_by_name = serializers.CharField(source='accessed_by.get_full_name', read_only=True)
    access_type_display = serializers.CharField(source='get_access_type_display', read_only=True)
    
    class Meta:
        model = RecordAccessLog
        fields = [
            'id', 'medical_record', 'accessed_by', 'accessed_by_name',
            'access_type', 'access_type_display', 'ip_address', 'timestamp'
        ]

class BlockchainStoreSerializer(serializers.Serializer):
    """
    Serializer for storing medical record on blockchain
    """
    record_id = serializers.UUIDField()
    patient_consent = serializers.BooleanField(
        help_text="Patient consent for storing on blockchain"
    )
    
    def validate_patient_consent(self, value):
        if not value:
            raise serializers.ValidationError(
                "Patient consent is required to store records on blockchain."
            )
        return value

class MedicalRecordRetrieveSerializer(serializers.Serializer):
    """
    Serializer for retrieving medical record by ID
    """
    access_reason = serializers.CharField(
        max_length=200,
        help_text="Reason for accessing this medical record"
    )
    
    def validate_access_reason(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError(
                "Please provide a detailed reason for accessing this record."
            )
        return value.strip()
