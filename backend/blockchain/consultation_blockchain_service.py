"""
Consultation Blockchain Service
Handles hashing and storing consultation data on blockchain
"""
import hashlib
import json
import logging
from datetime import datetime, timedelta
from django.utils import timezone
from django.conf import settings
from cryptography.fernet import Fernet
import secrets

from .models import (
    ConsultationBlockchainRecord, HealthcareProviderAccess,
    ConsultationAccessLog, BlockchainTransaction
)
from .services import BlockchainNetworkService

logger = logging.getLogger(__name__)

class ConsultationBlockchainService:
    """
    Service to handle consultation blockchain operations
    """
    
    def __init__(self):
        self.blockchain_service = BlockchainNetworkService()
        self.encryption_key = self._get_encryption_key()
    
    def hash_consultation(self, consultation):
        """
        Create blockchain hash for consultation data
        """
        try:
            # Create consultation data structure for hashing
            consultation_data = {
                'consultation_id': str(consultation.id),
                'patient_id': str(consultation.patient.id),
                'symptoms': consultation.symptoms_text,
                'ai_response': consultation.ai_response,
                'severity_score': consultation.severity_score,
                'emergency_detected': consultation.emergency_detected,
                'language': consultation.language,
                'created_at': consultation.created_at.isoformat(),
                'consultation_type': consultation.consultation_type
            }
            
            # Create individual hashes
            symptoms_hash = self._create_hash(consultation.symptoms_text)
            ai_response_hash = self._create_hash(consultation.ai_response)
            
            # Create master consultation hash
            consultation_json = json.dumps(consultation_data, sort_keys=True)
            consultation_hash = self._create_hash(consultation_json)
            
            # Create encryption key hash (for audit purposes)
            encryption_key_hash = self._create_hash(str(consultation.patient.id) + str(consultation.created_at))
            
            return {
                'consultation_hash': consultation_hash,
                'symptoms_hash': symptoms_hash,
                'ai_response_hash': ai_response_hash,
                'encryption_key_hash': encryption_key_hash,
                'data': consultation_data
            }
            
        except Exception as e:
            logger.error(f"Error hashing consultation {consultation.id}: {str(e)}")
            raise
    
    def store_consultation_on_blockchain(self, consultation):
        """
        Store consultation hash on blockchain and create blockchain record
        """
        try:
            # Check if already stored
            existing_record = ConsultationBlockchainRecord.objects.filter(
                consultation=consultation
            ).first()
            
            if existing_record and existing_record.stored_on_blockchain:
                logger.info(f"Consultation {consultation.id} already stored on blockchain")
                return existing_record
            
            # Generate hashes
            hash_data = self.hash_consultation(consultation)
            
            # Encrypt consultation data (optional, for sensitive data)
            encrypted_data = self._encrypt_consultation_data(hash_data['data'])
            
            # Create blockchain transaction
            tx_hash = self.blockchain_service.create_blockchain_transaction(
                'medical_record',
                hash_data['consultation_hash']
            )
            
            # Get blockchain transaction record
            blockchain_transaction = BlockchainTransaction.objects.filter(
                transaction_hash=tx_hash
            ).first()
            
            # Create or update consultation blockchain record
            if existing_record:
                consultation_record = existing_record
                consultation_record.consultation_hash = hash_data['consultation_hash']
                consultation_record.symptoms_hash = hash_data['symptoms_hash']
                consultation_record.ai_response_hash = hash_data['ai_response_hash']
                consultation_record.encryption_key_hash = hash_data['encryption_key_hash']
                consultation_record.blockchain_transaction = blockchain_transaction
                consultation_record.stored_on_blockchain = True
                consultation_record.save()
            else:
                consultation_record = ConsultationBlockchainRecord.objects.create(
                    consultation=consultation,
                    patient=consultation.patient,
                    consultation_hash=hash_data['consultation_hash'],
                    symptoms_hash=hash_data['symptoms_hash'],
                    ai_response_hash=hash_data['ai_response_hash'],
                    encryption_key_hash=hash_data['encryption_key_hash'],
                    blockchain_transaction=blockchain_transaction,
                    stored_on_blockchain=True,
                    encrypted=True
                )
            
            logger.info(f"Consultation {consultation.id} stored on blockchain with hash {consultation_record.consultation_hash}")
            return consultation_record
            
        except Exception as e:
            logger.error(f"Error storing consultation {consultation.id} on blockchain: {str(e)}")
            raise
    
    def grant_provider_access(self, patient, healthcare_provider, consultation_record, access_level='read_only', purpose='', expires_in_days=30):
        """
        Grant healthcare provider access to patient's consultation blockchain record
        """
        try:
            # Check if access already exists
            existing_access = HealthcareProviderAccess.objects.filter(
                patient=patient,
                healthcare_provider=healthcare_provider,
                consultation_record=consultation_record
            ).first()
            
            if existing_access and existing_access.access_status == 'approved':
                logger.info(f"Access already granted to {healthcare_provider.username} for consultation {consultation_record.consultation.id}")
                return existing_access
            
            # Create expiration date
            expires_at = timezone.now() + timedelta(days=expires_in_days)
            
            # Create access grant hash
            access_data = {
                'patient_id': str(patient.id),
                'provider_id': str(healthcare_provider.id),
                'consultation_hash': consultation_record.consultation_hash,
                'access_level': access_level,
                'purpose': purpose,
                'granted_at': timezone.now().isoformat(),
                'expires_at': expires_at.isoformat()
            }
            access_grant_hash = self._create_hash(json.dumps(access_data, sort_keys=True))
            
            # Create blockchain transaction for access grant
            tx_hash = self.blockchain_service.create_blockchain_transaction(
                'access_grant',
                access_grant_hash
            )
            
            # Get blockchain transaction record
            blockchain_transaction = BlockchainTransaction.objects.filter(
                transaction_hash=tx_hash
            ).first()
            
            # Create or update access record
            if existing_access:
                access_record = existing_access
                access_record.access_level = access_level
                access_record.access_status = 'approved'
                access_record.purpose = purpose
                access_record.granted_at = timezone.now()
                access_record.expires_at = expires_at
                access_record.access_grant_hash = access_grant_hash
                access_record.blockchain_transaction = blockchain_transaction
                access_record.save()
            else:
                access_record = HealthcareProviderAccess.objects.create(
                    patient=patient,
                    healthcare_provider=healthcare_provider,
                    consultation_record=consultation_record,
                    access_level=access_level,
                    access_status='approved',
                    purpose=purpose,
                    granted_at=timezone.now(),
                    expires_at=expires_at,
                    access_grant_hash=access_grant_hash,
                    blockchain_transaction=blockchain_transaction
                )
            
            logger.info(f"Access granted to {healthcare_provider.username} for consultation {consultation_record.consultation.id}")
            return access_record
            
        except Exception as e:
            logger.error(f"Error granting provider access: {str(e)}")
            raise
    
    def verify_provider_access(self, healthcare_provider, consultation_record):
        """
        Verify if healthcare provider has valid access to consultation record
        """
        try:
            access_record = HealthcareProviderAccess.objects.filter(
                healthcare_provider=healthcare_provider,
                consultation_record=consultation_record,
                access_status='approved',
                expires_at__gt=timezone.now()
            ).first()
            
            if access_record:
                return {
                    'has_access': True,
                    'access_level': access_record.access_level,
                    'expires_at': access_record.expires_at,
                    'purpose': access_record.purpose,
                    'access_record': access_record
                }
            else:
                return {
                    'has_access': False,
                    'message': 'No valid access found or access expired'
                }
                
        except Exception as e:
            logger.error(f"Error verifying provider access: {str(e)}")
            return {
                'has_access': False,
                'message': f'Error verifying access: {str(e)}'
            }
    
    def log_consultation_access(self, consultation_record, accessed_by, request, provider_access=None):
        """
        Log access to consultation blockchain record
        """
        try:
            # Determine access type
            if accessed_by == consultation_record.patient:
                access_type = 'patient'
            elif provider_access:
                access_type = 'healthcare_provider'
            else:
                access_type = 'emergency'
            
            # Create access log
            access_log = ConsultationAccessLog.objects.create(
                consultation_record=consultation_record,
                accessed_by=accessed_by,
                provider_access=provider_access,
                access_type=access_type,
                ip_address=self._get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                access_verified_on_blockchain=False  # Can be updated later with blockchain verification
            )
            
            logger.info(f"Access logged for consultation {consultation_record.consultation.id} by {accessed_by.username}")
            return access_log
            
        except Exception as e:
            logger.error(f"Error logging consultation access: {str(e)}")
            raise
    
    def get_patient_consultation_records(self, patient):
        """
        Get all blockchain records for patient's consultations
        """
        try:
            return ConsultationBlockchainRecord.objects.filter(
                patient=patient,
                stored_on_blockchain=True
            ).order_by('-created_at')
            
        except Exception as e:
            logger.error(f"Error getting patient consultation records: {str(e)}")
            raise
    
    def get_provider_accessible_records(self, healthcare_provider):
        """
        Get all consultation records accessible by healthcare provider
        """
        try:
            # Get all approved accesses for this provider
            approved_accesses = HealthcareProviderAccess.objects.filter(
                healthcare_provider=healthcare_provider,
                access_status='approved',
                expires_at__gt=timezone.now()
            ).select_related('consultation_record')
            
            return [access.consultation_record for access in approved_accesses]
            
        except Exception as e:
            logger.error(f"Error getting provider accessible records: {str(e)}")
            raise
    
    def revoke_provider_access(self, patient, healthcare_provider, consultation_record):
        """
        Revoke healthcare provider's access to consultation record
        """
        try:
            access_record = HealthcareProviderAccess.objects.filter(
                patient=patient,
                healthcare_provider=healthcare_provider,
                consultation_record=consultation_record,
                access_status='approved'
            ).first()
            
            if access_record:
                access_record.access_status = 'revoked'
                access_record.revoked_at = timezone.now()
                access_record.save()
                
                logger.info(f"Access revoked for {healthcare_provider.username} to consultation {consultation_record.consultation.id}")
                return True
            else:
                logger.warning(f"No active access found to revoke")
                return False
                
        except Exception as e:
            logger.error(f"Error revoking provider access: {str(e)}")
            raise
    
    def verify_consultation_integrity(self, consultation_record):
        """
        Verify consultation data integrity using blockchain hash
        """
        try:
            # Rehash current consultation data
            current_hash_data = self.hash_consultation(consultation_record.consultation)
            
            # Compare with stored hash
            integrity_verified = (
                current_hash_data['consultation_hash'] == consultation_record.consultation_hash and
                current_hash_data['symptoms_hash'] == consultation_record.symptoms_hash and
                current_hash_data['ai_response_hash'] == consultation_record.ai_response_hash
            )
            
            return {
                'verified': integrity_verified,
                'stored_hash': consultation_record.consultation_hash,
                'current_hash': current_hash_data['consultation_hash'],
                'message': 'Data integrity verified' if integrity_verified else 'Data integrity compromised'
            }
            
        except Exception as e:
            logger.error(f"Error verifying consultation integrity: {str(e)}")
            return {
                'verified': False,
                'message': f'Integrity verification failed: {str(e)}'
            }
    
    def _create_hash(self, data):
        """
        Create SHA-256 hash of data
        """
        return hashlib.sha256(str(data).encode()).hexdigest()
    
    def _get_encryption_key(self):
        """
        Get or create encryption key for consultation data
        """
        # In production, this should be stored securely
        key = getattr(settings, 'CONSULTATION_ENCRYPTION_KEY', None)
        if not key:
            key = Fernet.generate_key()
        return key
    
    def _encrypt_consultation_data(self, data):
        """
        Encrypt consultation data
        """
        try:
            fernet = Fernet(self.encryption_key)
            data_json = json.dumps(data)
            encrypted_data = fernet.encrypt(data_json.encode())
            return encrypted_data.decode()
        except Exception as e:
            logger.error(f"Error encrypting consultation data: {str(e)}")
            return None
    
    def _decrypt_consultation_data(self, encrypted_data):
        """
        Decrypt consultation data
        """
        try:
            fernet = Fernet(self.encryption_key)
            decrypted_data = fernet.decrypt(encrypted_data.encode())
            return json.loads(decrypted_data.decode())
        except Exception as e:
            logger.error(f"Error decrypting consultation data: {str(e)}")
            return None
    
    def _get_client_ip(self, request):
        """
        Get client IP address from request
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
        return ip
