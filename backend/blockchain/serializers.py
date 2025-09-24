from rest_framework import serializers
from .models import (
    BlockchainTransaction, MedicineVerification, 
    SmartContract, PatientConsentRecord
)

class BlockchainTransactionSerializer(serializers.ModelSerializer):
    """
    Serializer for blockchain transactions
    """
    transaction_type_display = serializers.CharField(source='get_transaction_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = BlockchainTransaction
        fields = [
            'id', 'transaction_type', 'transaction_type_display',
            'transaction_hash', 'block_number', 'contract_address',
            'data_hash', 'gas_used', 'gas_price', 'transaction_fee',
            'status', 'status_display', 'error_message', 'created_at',
            'confirmed_at'
        ]
        read_only_fields = ['id', 'created_at', 'confirmed_at']

class MedicineVerificationSerializer(serializers.ModelSerializer):
    """
    Serializer for medicine verification
    """
    verification_status_display = serializers.CharField(source='get_verification_status_display', read_only=True)
    is_expired = serializers.SerializerMethodField()
    
    class Meta:
        model = MedicineVerification
        fields = [
            'id', 'medicine_name', 'batch_number', 'manufacturer',
            'expiry_date', 'is_expired', 'qr_code', 'verification_status',
            'verification_status_display', 'blockchain_verified',
            'created_at', 'verified_at'
        ]
        read_only_fields = [
            'id', 'verification_status', 'blockchain_verified',
            'created_at', 'verified_at'
        ]
    
    def get_is_expired(self, obj):
        from datetime import date
        return obj.expiry_date < date.today() if obj.expiry_date else False

class MedicineVerificationCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating medicine verification requests
    """
    class Meta:
        model = MedicineVerification
        fields = [
            'medicine_name', 'batch_number', 'manufacturer',
            'expiry_date', 'qr_code'
        ]
    
    def validate_qr_code(self, value):
        if len(value) < 10:
            raise serializers.ValidationError(
                "QR code should be at least 10 characters long"
            )
        return value

class QRCodeVerificationSerializer(serializers.Serializer):
    """
    Serializer for QR code verification requests
    """
    qr_code = serializers.CharField(
        max_length=500,
        help_text="QR code data from medicine package"
    )
    
    def validate_qr_code(self, value):
        if not value.strip():
            raise serializers.ValidationError("QR code is required")
        if len(value.strip()) < 5:
            raise serializers.ValidationError("Invalid QR code format")
        return value.strip()

class SmartContractSerializer(serializers.ModelSerializer):
    """
    Serializer for smart contracts
    """
    contract_type_display = serializers.CharField(source='get_contract_type_display', read_only=True)
    network_display = serializers.CharField(source='get_network_display', read_only=True)
    
    class Meta:
        model = SmartContract
        fields = [
            'id', 'contract_type', 'contract_type_display',
            'contract_address', 'network', 'network_display',
            'deployment_transaction', 'deployed_at', 'is_active',
            'version'
        ]
        read_only_fields = ['id', 'deployed_at']

class PatientConsentRecordSerializer(serializers.ModelSerializer):
    """
    Serializer for patient consent records
    """
    patient_name = serializers.CharField(source='patient.get_full_name', read_only=True)
    consent_type_display = serializers.CharField(source='get_consent_type_display', read_only=True)
    is_active = serializers.SerializerMethodField()
    
    class Meta:
        model = PatientConsentRecord
        fields = [
            'id', 'patient', 'patient_name', 'consent_type',
            'consent_type_display', 'granted', 'consent_text',
            'digital_signature', 'consent_hash', 'is_active',
            'created_at', 'expires_at', 'revoked_at'
        ]
        read_only_fields = [
            'id', 'patient', 'consent_hash', 'created_at'
        ]
    
    def get_is_active(self, obj):
        from django.utils import timezone
        now = timezone.now()
        
        # Check if consent is revoked
        if obj.revoked_at:
            return False
        
        # Check if consent is expired
        if obj.expires_at and obj.expires_at < now:
            return False
        
        return obj.granted

class ConsentCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating consent records
    """
    class Meta:
        model = PatientConsentRecord
        fields = [
            'consent_type', 'granted', 'consent_text',
            'digital_signature', 'expires_at'
        ]
    
    def validate_consent_text(self, value):
        if len(value.strip()) < 20:
            raise serializers.ValidationError(
                "Consent text should be at least 20 characters long"
            )
        return value.strip()

class BlockchainStatusSerializer(serializers.Serializer):
    """
    Serializer for blockchain network status
    """
    network_name = serializers.CharField()
    is_connected = serializers.BooleanField()
    latest_block = serializers.IntegerField()
    gas_price = serializers.CharField()
    account_balance = serializers.CharField()
    
class TransactionStatusSerializer(serializers.Serializer):
    """
    Serializer for transaction status checks
    """
    transaction_hash = serializers.CharField(
        max_length=66,
        help_text="Blockchain transaction hash to check"
    )
    
    def validate_transaction_hash(self, value):
        if not value.startswith('0x') or len(value) != 66:
            raise serializers.ValidationError(
                "Invalid transaction hash format"
            )
        return value
