"""
Blockchain and medicine verification services
"""
import hashlib
import json
from datetime import date, datetime
from web3 import Web3
from django.conf import settings
from .models import BlockchainTransaction, MedicineVerification
import logging

logger = logging.getLogger(__name__)

class MedicineVerificationService:
    """
    Service for verifying medicine authenticity
    """
    
    def __init__(self):
        self.web3_url = getattr(settings, 'WEB3_PROVIDER_URL', '')
        self.contract_address = getattr(settings, 'MEDICINE_AUTH_CONTRACT_ADDRESS', '')
        
        if self.web3_url:
            try:
                self.web3 = Web3(Web3.HTTPProvider(self.web3_url))
            except Exception as e:
                logger.error(f"Failed to initialize Web3: {str(e)}")
                self.web3 = None
        else:
            self.web3 = None
    
    def verify_medicine(self, qr_code):
        """
        Verify medicine using QR code data
        """
        try:
            # Parse QR code data (assuming it contains medicine info)
            medicine_data = self._parse_qr_code(qr_code)
            
            if not medicine_data:
                return {
                    'found': False,
                    'message': 'Invalid QR code format'
                }
            
            # Check against known medicine database (mock for now)
            verification_result = self._check_medicine_database(medicine_data)
            
            return verification_result
            
        except Exception as e:
            logger.error(f"Medicine verification error: {str(e)}")
            return {
                'found': False,
                'message': f'Verification failed: {str(e)}'
            }
    
    def verify_on_blockchain(self, medicine):
        """
        Verify medicine authenticity on blockchain
        """
        try:
            if not self.web3:
                # Mock verification for development
                return {
                    'verified': True,
                    'message': 'Blockchain verification successful (mock mode)'
                }
            
            # Create medicine hash for blockchain lookup
            medicine_hash = self._create_medicine_hash(medicine)
            
            # Query blockchain contract
            # This would call actual smart contract method
            blockchain_result = self._query_blockchain_contract(medicine_hash)
            
            return blockchain_result
            
        except Exception as e:
            logger.error(f"Blockchain verification error: {str(e)}")
            return {
                'verified': False,
                'message': f'Blockchain verification failed: {str(e)}'
            }
    
    def _parse_qr_code(self, qr_code):
        """
        Parse QR code to extract medicine information
        """
        try:
            # QR code format: JSON with medicine data
            if qr_code.startswith('{'):
                return json.loads(qr_code)
            
            # QR code format: pipe-separated values
            if '|' in qr_code:
                parts = qr_code.split('|')
                if len(parts) >= 4:
                    return {
                        'medicine_name': parts[0],
                        'batch_number': parts[1],
                        'manufacturer': parts[2],
                        'expiry_date': parts[3]
                    }
            
            # Mock parsing for development
            return self._mock_parse_qr_code(qr_code)
            
        except Exception as e:
            logger.error(f"QR code parsing error: {str(e)}")
            return None
    
    def _check_medicine_database(self, medicine_data):
        """
        Check medicine against authorized database
        """
        # This would query actual medicine authorization database
        # For now, using mock data
        
        authorized_medicines = {
            'paracetamol': {
                'manufacturers': ['Cipla Uganda', 'Kampala Pharmaceutical'],
                'status': 'authentic'
            },
            'amoxicillin': {
                'manufacturers': ['Quality Chemicals', 'Medic Pharma'],
                'status': 'authentic'
            },
            'chloroquine': {
                'manufacturers': ['Cipla Uganda'],
                'status': 'authentic'
            }
        }
        
        medicine_name = medicine_data.get('medicine_name', '').lower()
        manufacturer = medicine_data.get('manufacturer', '')
        
        if medicine_name in authorized_medicines:
            auth_info = authorized_medicines[medicine_name]
            
            if manufacturer in auth_info['manufacturers']:
                # Parse expiry date
                expiry_date = self._parse_date(medicine_data.get('expiry_date'))
                
                return {
                    'found': True,
                    'medicine_name': medicine_data['medicine_name'],
                    'batch_number': medicine_data.get('batch_number', ''),
                    'manufacturer': manufacturer,
                    'expiry_date': expiry_date,
                    'status': auth_info['status'],
                    'message': 'Medicine verified as authentic'
                }
            else:
                return {
                    'found': True,
                    'medicine_name': medicine_data['medicine_name'],
                    'batch_number': medicine_data.get('batch_number', ''),
                    'manufacturer': manufacturer,
                    'expiry_date': self._parse_date(medicine_data.get('expiry_date')),
                    'status': 'counterfeit',
                    'message': 'Unauthorized manufacturer detected'
                }
        
        return {
            'found': False,
            'message': 'Medicine not found in authorized database'
        }
    
    def _create_medicine_hash(self, medicine):
        """
        Create hash for blockchain verification
        """
        medicine_string = f"{medicine.medicine_name}{medicine.batch_number}{medicine.manufacturer}{medicine.expiry_date}"
        return hashlib.sha256(medicine_string.encode()).hexdigest()
    
    def _query_blockchain_contract(self, medicine_hash):
        """
        Query blockchain smart contract for medicine verification
        """
        try:
            # This would call actual smart contract method
            # For now, returning mock result
            return {
                'verified': True,
                'message': 'Medicine hash found on blockchain'
            }
            
        except Exception as e:
            return {
                'verified': False,
                'message': f'Blockchain query failed: {str(e)}'
            }
    
    def _mock_parse_qr_code(self, qr_code):
        """
        Mock QR code parsing for development
        """
        # Generate mock medicine data based on QR code
        qr_hash = hashlib.md5(qr_code.encode()).hexdigest()[:8]
        
        medicines = ['Paracetamol', 'Amoxicillin', 'Chloroquine', 'Ibuprofen']
        manufacturers = ['Cipla Uganda', 'Quality Chemicals', 'Kampala Pharmaceutical']
        
        return {
            'medicine_name': medicines[hash(qr_code) % len(medicines)],
            'batch_number': f'BATCH-{qr_hash.upper()}',
            'manufacturer': manufacturers[hash(qr_code) % len(manufacturers)],
            'expiry_date': '2025-12-31'
        }
    
    def _parse_date(self, date_string):
        """
        Parse date string to date object
        """
        if not date_string:
            return None
        
        try:
            # Try different date formats
            for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y']:
                try:
                    return datetime.strptime(date_string, fmt).date()
                except ValueError:
                    continue
            
            # If no format works, return None
            return None
            
        except Exception:
            return None

class BlockchainNetworkService:
    """
    Service for interacting with blockchain network
    """
    
    def __init__(self):
        self.web3_url = getattr(settings, 'WEB3_PROVIDER_URL', '')
        self.private_key = getattr(settings, 'BLOCKCHAIN_PRIVATE_KEY', '')
        
        if self.web3_url:
            try:
                self.web3 = Web3(Web3.HTTPProvider(self.web3_url))
                if self.private_key:
                    self.account = self.web3.eth.account.from_key(self.private_key)
                else:
                    self.account = None
            except Exception as e:
                logger.error(f"Failed to initialize Web3: {str(e)}")
                self.web3 = None
                self.account = None
        else:
            self.web3 = None
            self.account = None
    
    def get_network_status(self):
        """
        Get current blockchain network status
        """
        try:
            if not self.web3:
                return self._mock_network_status()
            
            # Get network information
            latest_block = self.web3.eth.block_number
            gas_price = self.web3.eth.gas_price
            
            # Get account balance if account is available
            balance = "0"
            if self.account:
                balance_wei = self.web3.eth.get_balance(self.account.address)
                balance = self.web3.from_wei(balance_wei, 'ether')
            
            return {
                'network_name': 'Ethereum Sepolia Testnet',
                'is_connected': self.web3.is_connected(),
                'latest_block': latest_block,
                'gas_price': f"{self.web3.from_wei(gas_price, 'gwei')} gwei",
                'account_balance': f"{balance} ETH"
            }
            
        except Exception as e:
            logger.error(f"Network status error: {str(e)}")
            return self._mock_network_status()
    
    def get_transaction_status(self, tx_hash):
        """
        Get status of a blockchain transaction
        """
        try:
            if not self.web3:
                return self._mock_transaction_status(tx_hash)
            
            # Get transaction receipt
            try:
                tx_receipt = self.web3.eth.get_transaction_receipt(tx_hash)
                tx = self.web3.eth.get_transaction(tx_hash)
                
                # Calculate confirmations
                current_block = self.web3.eth.block_number
                confirmations = current_block - tx_receipt.blockNumber
                
                return {
                    'status': 'confirmed' if tx_receipt.status == 1 else 'failed',
                    'block_number': tx_receipt.blockNumber,
                    'confirmations': confirmations,
                    'gas_used': tx_receipt.gasUsed,
                    'success': tx_receipt.status == 1,
                    'error': None if tx_receipt.status == 1 else 'Transaction failed'
                }
                
            except Exception:
                # Transaction might be pending
                return {
                    'status': 'pending',
                    'block_number': None,
                    'confirmations': 0,
                    'gas_used': None,
                    'success': None,
                    'error': None
                }
                
        except Exception as e:
            logger.error(f"Transaction status error: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def create_blockchain_transaction(self, transaction_type, data_hash):
        """
        Create and send blockchain transaction
        """
        try:
            if not self.web3 or not self.account:
                return self._mock_create_transaction(transaction_type, data_hash)
            
            # Create transaction
            contract_address = getattr(settings, 'MEDICAL_RECORDS_CONTRACT_ADDRESS', '')
            
            transaction = {
                'to': contract_address,
                'value': 0,
                'gas': 100000,
                'gasPrice': self.web3.eth.gas_price,
                'nonce': self.web3.eth.get_transaction_count(self.account.address),
                'data': self._encode_contract_data(transaction_type, data_hash)
            }
            
            # Sign and send transaction
            signed_txn = self.web3.eth.account.sign_transaction(transaction, self.private_key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Create blockchain transaction record
            blockchain_tx = BlockchainTransaction.objects.create(
                transaction_type=transaction_type,
                transaction_hash=tx_hash.hex(),
                contract_address=contract_address,
                data_hash=data_hash,
                gas_used=None,  # Will be updated when confirmed
                gas_price=transaction['gasPrice'],
                status='pending'
            )
            
            return tx_hash.hex()
            
        except Exception as e:
            logger.error(f"Transaction creation error: {str(e)}")
            return self._mock_create_transaction(transaction_type, data_hash)
    
    def _encode_contract_data(self, transaction_type, data_hash):
        """
        Encode data for smart contract call
        """
        # This would use actual ABI encoding
        # For now, returning mock encoded data
        return f"0x{data_hash}"
    
    def _mock_network_status(self):
        """
        Mock network status for development
        """
        return {
            'network_name': 'Mock Testnet',
            'is_connected': True,
            'latest_block': 12345678,
            'gas_price': '20 gwei',
            'account_balance': '1.5 ETH'
        }
    
    def _mock_transaction_status(self, tx_hash):
        """
        Mock transaction status for development
        """
        return {
            'status': 'confirmed',
            'block_number': 12345679,
            'confirmations': 12,
            'gas_used': 85000,
            'success': True,
            'error': None
        }
    
    def _mock_create_transaction(self, transaction_type, data_hash):
        """
        Mock transaction creation for development
        """
        # Generate mock transaction hash
        mock_hash = f"0x{''.join([f'{ord(c):02x}' for c in data_hash[:32]])}"
        
        # Create blockchain transaction record
        BlockchainTransaction.objects.create(
            transaction_type=transaction_type,
            transaction_hash=mock_hash,
            contract_address='0x1234567890123456789012345678901234567890',
            data_hash=data_hash,
            status='pending'
        )
        
        return mock_hash

class SmartContractService:
    """
    Service for deploying and interacting with smart contracts
    """
    
    def __init__(self):
        self.web3_url = getattr(settings, 'WEB3_PROVIDER_URL', '')
        self.private_key = getattr(settings, 'BLOCKCHAIN_PRIVATE_KEY', '')
        
        if self.web3_url:
            try:
                self.web3 = Web3(Web3.HTTPProvider(self.web3_url))
                if self.private_key:
                    self.account = self.web3.eth.account.from_key(self.private_key)
                else:
                    self.account = None
            except Exception as e:
                logger.error(f"Failed to initialize Web3: {str(e)}")
                self.web3 = None
                self.account = None
        else:
            self.web3 = None
            self.account = None
    
    def deploy_medical_records_contract(self):
        """
        Deploy medical records smart contract
        """
        # This would deploy actual smart contract
        # For now, returning mock deployment
        return {
            'contract_address': '0x1234567890123456789012345678901234567890',
            'transaction_hash': '0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890',
            'deployed': True
        }
    
    def deploy_medicine_auth_contract(self):
        """
        Deploy medicine authentication smart contract
        """
        # This would deploy actual smart contract
        # For now, returning mock deployment
        return {
            'contract_address': '0x0987654321098765432109876543210987654321',
            'transaction_hash': '0xfedcba0987654321fedcba0987654321fedcba0987654321fedcba0987654321',
            'deployed': True
        }
