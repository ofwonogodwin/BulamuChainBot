from django.db import models
from django.utils import timezone
import uuid

class BlockchainTransaction(models.Model):
    """
    Model to track blockchain transactions for medical records and medicine verification
    """
    TRANSACTION_TYPES = [
        ('medical_record', 'Medical Record Storage'),
        ('medicine_verification', 'Medicine Verification'),
        ('patient_consent', 'Patient Consent'),
        ('access_grant', 'Access Grant'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaction_type = models.CharField(max_length=30, choices=TRANSACTION_TYPES)
    
    # Blockchain data
    transaction_hash = models.CharField(max_length=66, unique=True)
    block_number = models.BigIntegerField(null=True, blank=True)
    contract_address = models.CharField(max_length=42)
    
    # Data hash stored on blockchain
    data_hash = models.CharField(max_length=64)
    
    # Gas and fees
    gas_used = models.BigIntegerField(null=True, blank=True)
    gas_price = models.BigIntegerField(null=True, blank=True)
    transaction_fee = models.DecimalField(max_digits=20, decimal_places=18, null=True, blank=True)
    
    # Status and metadata
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['transaction_hash']),
            models.Index(fields=['data_hash']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.transaction_type}: {self.transaction_hash[:10]}... ({self.status})"

class MedicineVerification(models.Model):
    """
    Model to store medicine verification data
    """
    VERIFICATION_STATUS = [
        ('authentic', 'Authentic'),
        ('counterfeit', 'Counterfeit'),
        ('unknown', 'Unknown'),
        ('pending', 'Pending Verification'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Medicine information
    medicine_name = models.CharField(max_length=200)
    batch_number = models.CharField(max_length=100)
    manufacturer = models.CharField(max_length=200)
    expiry_date = models.DateField()
    qr_code = models.CharField(max_length=500, unique=True)
    
    # Verification
    verification_status = models.CharField(max_length=15, choices=VERIFICATION_STATUS, default='pending')
    blockchain_verified = models.BooleanField(default=False)
    verification_transaction = models.ForeignKey(BlockchainTransaction, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(default=timezone.now)
    verified_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['qr_code']),
            models.Index(fields=['batch_number']),
        ]
    
    def __str__(self):
        return f"{self.medicine_name} - {self.batch_number} ({self.verification_status})"

class SmartContract(models.Model):
    """
    Model to track deployed smart contracts
    """
    CONTRACT_TYPES = [
        ('medical_records', 'Medical Records Contract'),
        ('medicine_auth', 'Medicine Authentication Contract'),
        ('patient_consent', 'Patient Consent Contract'),
    ]
    
    NETWORKS = [
        ('ethereum_mainnet', 'Ethereum Mainnet'),
        ('ethereum_sepolia', 'Ethereum Sepolia Testnet'),
        ('polygon_mainnet', 'Polygon Mainnet'),
        ('polygon_mumbai', 'Polygon Mumbai Testnet'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contract_type = models.CharField(max_length=20, choices=CONTRACT_TYPES)
    contract_address = models.CharField(max_length=42, unique=True)
    network = models.CharField(max_length=20, choices=NETWORKS)
    
    # Contract details
    abi = models.JSONField()  # Contract ABI
    bytecode = models.TextField()
    deployment_transaction = models.CharField(max_length=66)
    
    # Metadata
    deployed_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    version = models.CharField(max_length=10, default='1.0')
    
    class Meta:
        unique_together = ['contract_type', 'network']
    
    def __str__(self):
        return f"{self.contract_type} on {self.network}: {self.contract_address}"

class PatientConsentRecord(models.Model):
    """
    Model to track patient consent for data sharing on blockchain
    """
    CONSENT_TYPES = [
        ('data_storage', 'Data Storage on Blockchain'),
        ('data_sharing', 'Data Sharing with Healthcare Providers'),
        ('research', 'Research Participation'),
        ('emergency_access', 'Emergency Access'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey('authsystem.CustomUser', on_delete=models.CASCADE, related_name='consent_records')
    consent_type = models.CharField(max_length=20, choices=CONSENT_TYPES)
    
    # Consent details
    granted = models.BooleanField(default=False)
    consent_text = models.TextField()
    digital_signature = models.CharField(max_length=200, blank=True)
    
    # Blockchain tracking
    blockchain_transaction = models.ForeignKey(BlockchainTransaction, on_delete=models.SET_NULL, null=True, blank=True)
    consent_hash = models.CharField(max_length=64)
    
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(null=True, blank=True)
    revoked_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['patient', 'consent_type']
        indexes = [
            models.Index(fields=['patient', 'consent_type']),
            models.Index(fields=['consent_hash']),
        ]
    
    def __str__(self):
        status = "Granted" if self.granted else "Denied"
        return f"{self.patient.username} - {self.consent_type}: {status}"
