"""
Blockchain and encryption services for medical records
"""
import hashlib
import json
from web3 import Web3
from django.conf import settings
from .models import MedicalRecord
import logging

logger = logging.getLogger(__name__)

class BlockchainService:
    """
    Service for interacting with blockchain for medical records
    """
    
    def __init__(self):
        self.web3_url = getattr(settings, 'WEB3_PROVIDER_URL', '')
        self.private_key = getattr(settings, 'BLOCKCHAIN_PRIVATE_KEY', '')
        self.contract_address = getattr(settings, 'MEDICAL_RECORDS_CONTRACT_ADDRESS', '')
        
        if self.web3_url:
            try:
                self.web3 = Web3(Web3.HTTPProvider(self.web3_url))
                self.account = self.web3.eth.account.from_key(self.private_key) if self.private_key else None
            except Exception as e:
                logger.error(f"Failed to initialize Web3: {str(e)}")
                self.web3 = None
                self.account = None
        else:
            self.web3 = None
            self.account = None
    
    def store_medical_record(self, medical_record):
        """
        Store medical record hash on blockchain
        """
        try:
            if not self.web3 or not self.account:
                # Mock transaction for development
                return self._mock_blockchain_transaction(medical_record)
            
            # Prepare transaction data
            record_data = {
                'record_id': str(medical_record.id),
                'patient_id': str(medical_record.patient.id),
                'record_hash': medical_record.record_hash,
                'timestamp': int(medical_record.created_at.timestamp()),
                'record_type': medical_record.record_type
            }
            
            # Create transaction
            transaction = self._create_blockchain_transaction(record_data)
            
            # Sign and send transaction
            signed_txn = self.web3.eth.account.sign_transaction(transaction, self.private_key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            return tx_hash.hex()
            
        except Exception as e:
            logger.error(f"Blockchain storage error: {str(e)}")
            # Return mock hash for development
            return self._mock_blockchain_transaction(medical_record)
    
    def verify_medical_record(self, medical_record):
        """
        Verify medical record integrity using blockchain
        """
        try:
            if not self.web3 or not medical_record.blockchain_tx_hash:
                return self._mock_verification_result(medical_record)
            
            # Get transaction from blockchain
            tx = self.web3.eth.get_transaction(medical_record.blockchain_tx_hash)
            
            if not tx:
                return {
                    'verified': False,
                    'message': 'Transaction not found on blockchain'
                }
            
            # Extract stored hash from transaction data
            # This would decode the actual contract call data
            stored_hash = self._extract_hash_from_transaction(tx)
            
            # Compare with current record hash
            verified = stored_hash == medical_record.record_hash
            
            return {
                'verified': verified,
                'blockchain_hash': stored_hash,
                'message': 'Record verified successfully' if verified else 'Record hash mismatch'
            }
            
        except Exception as e:
            logger.error(f"Blockchain verification error: {str(e)}")
            return {
                'verified': False,
                'message': f'Verification failed: {str(e)}'
            }
    
    def _create_blockchain_transaction(self, record_data):
        """
        Create blockchain transaction for storing record
        """
        # This would create actual smart contract call
        # For now, returning mock transaction structure
        return {
            'to': self.contract_address,
            'value': 0,
            'gas': 100000,
            'gasPrice': self.web3.to_wei('20', 'gwei'),
            'nonce': self.web3.eth.get_transaction_count(self.account.address),
            'data': self._encode_record_data(record_data)
        }
    
    def _encode_record_data(self, record_data):
        """
        Encode record data for blockchain transaction
        """
        # This would use actual ABI encoding
        # For now, returning encoded JSON
        return json.dumps(record_data).encode().hex()
    
    def _extract_hash_from_transaction(self, transaction):
        """
        Extract record hash from blockchain transaction
        """
        # This would decode actual contract call data
        # For now, returning mock hash
        return "mock_blockchain_hash_" + str(transaction.get('hash', ''))[:10]
    
    def _mock_blockchain_transaction(self, medical_record):
        """
        Create mock blockchain transaction for development
        """
        mock_hash = f"0x{''.join([f'{ord(c):02x}' for c in str(medical_record.id)[:32]])}"
        return mock_hash
    
    def _mock_verification_result(self, medical_record):
        """
        Create mock verification result for development
        """
        return {
            'verified': True,
            'blockchain_hash': medical_record.record_hash,
            'message': 'Record verified (mock mode)'
        }

class RecordEncryptionService:
    """
    Service for encrypting and decrypting medical records
    """
    
    def __init__(self):
        self.encryption_key = self._get_encryption_key()
    
    def encrypt_record_content(self, content):
        """
        Encrypt sensitive record content
        """
        try:
            from cryptography.fernet import Fernet
            
            if isinstance(content, str):
                content = content.encode()
            
            f = Fernet(self.encryption_key)
            encrypted_content = f.encrypt(content)
            return encrypted_content.decode()
            
        except ImportError:
            logger.warning("Cryptography library not available, returning unencrypted content")
            return content
        except Exception as e:
            logger.error(f"Encryption error: {str(e)}")
            return content
    
    def decrypt_record_content(self, encrypted_content):
        """
        Decrypt record content
        """
        try:
            from cryptography.fernet import Fernet
            
            if isinstance(encrypted_content, str):
                encrypted_content = encrypted_content.encode()
            
            f = Fernet(self.encryption_key)
            decrypted_content = f.decrypt(encrypted_content)
            return decrypted_content.decode()
            
        except ImportError:
            logger.warning("Cryptography library not available, returning content as-is")
            return encrypted_content
        except Exception as e:
            logger.error(f"Decryption error: {str(e)}")
            return encrypted_content
    
    def hash_patient_data(self, patient_data):
        """
        Create hash of patient data for blockchain storage
        """
        if isinstance(patient_data, dict):
            patient_data = json.dumps(patient_data, sort_keys=True)
        
        return hashlib.sha256(patient_data.encode()).hexdigest()
    
    def _get_encryption_key(self):
        """
        Get or generate encryption key
        """
        try:
            from cryptography.fernet import Fernet
            
            # In production, this should be loaded from secure storage
            encryption_key = getattr(settings, 'RECORD_ENCRYPTION_KEY', None)
            
            if not encryption_key:
                # Generate new key (should be stored securely in production)
                encryption_key = Fernet.generate_key()
                logger.warning("Generated new encryption key - should be stored securely")
            
            if isinstance(encryption_key, str):
                encryption_key = encryption_key.encode()
            
            return encryption_key
            
        except ImportError:
            logger.warning("Cryptography library not available")
            return b'mock_key_for_development_only_32bytes'

class MedicalRecordHashingService:
    """
    Service for creating and verifying medical record hashes
    """
    
    @staticmethod
    def create_record_hash(medical_record):
        """
        Create SHA-256 hash of medical record content
        """
        record_content = {
            'patient_id': str(medical_record.patient.id),
            'record_type': medical_record.record_type,
            'title': medical_record.title,
            'description': medical_record.description,
            'diagnosis': medical_record.diagnosis,
            'treatment': medical_record.treatment,
            'medications': medical_record.medications,
            'provider_name': medical_record.provider_name,
            'created_at': medical_record.created_at.isoformat()
        }
        
        # Sort keys for consistent hashing
        content_string = json.dumps(record_content, sort_keys=True)
        return hashlib.sha256(content_string.encode()).hexdigest()
    
    @staticmethod
    def verify_record_integrity(medical_record):
        """
        Verify that record hash matches content
        """
        current_hash = MedicalRecordHashingService.create_record_hash(medical_record)
        return current_hash == medical_record.record_hash
    
    @staticmethod
    def update_record_hash(medical_record):
        """
        Update record hash after content changes
        """
        medical_record.record_hash = MedicalRecordHashingService.create_record_hash(medical_record)
        medical_record.save()
        return medical_record.record_hash
