from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from .models import (
    BlockchainTransaction, MedicineVerification,
    SmartContract, PatientConsentRecord
)
from .serializers import (
    BlockchainTransactionSerializer, MedicineVerificationSerializer,
    MedicineVerificationCreateSerializer, QRCodeVerificationSerializer,
    SmartContractSerializer, PatientConsentRecordSerializer,
    ConsentCreateSerializer, BlockchainStatusSerializer,
    TransactionStatusSerializer
)
from .services import MedicineVerificationService, BlockchainNetworkService

User = get_user_model()

class MedicineVerificationView(APIView):
    """
    Verify medicine authenticity via QR code
    POST /api/medicine/verify
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = QRCodeVerificationSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            qr_code = serializer.validated_data['qr_code']
            
            # Check if medicine is already in our database
            try:
                medicine = MedicineVerification.objects.get(qr_code=qr_code)
                
                # Return existing verification result
                response_data = {
                    'medicine_name': medicine.medicine_name,
                    'batch_number': medicine.batch_number,
                    'manufacturer': medicine.manufacturer,
                    'expiry_date': medicine.expiry_date,
                    'verification_status': medicine.verification_status,
                    'blockchain_verified': medicine.blockchain_verified,
                    'verified_at': medicine.verified_at,
                    'message': 'Medicine verification retrieved from database'
                }
                
                # Check if expired
                from datetime import date
                if medicine.expiry_date and medicine.expiry_date < date.today():
                    response_data['warning'] = 'Medicine has expired'
                
                return Response(response_data)
                
            except MedicineVerification.DoesNotExist:
                # Verify medicine using blockchain and external services
                verification_service = MedicineVerificationService()
                verification_result = verification_service.verify_medicine(qr_code)
                
                if verification_result['found']:
                    # Create verification record
                    medicine = MedicineVerification.objects.create(
                        medicine_name=verification_result['medicine_name'],
                        batch_number=verification_result['batch_number'],
                        manufacturer=verification_result['manufacturer'],
                        expiry_date=verification_result['expiry_date'],
                        qr_code=qr_code,
                        verification_status=verification_result['status']
                    )
                    
                    # Try blockchain verification
                    blockchain_result = verification_service.verify_on_blockchain(medicine)
                    medicine.blockchain_verified = blockchain_result['verified']
                    medicine.save()
                    
                    response_data = {
                        'medicine_name': medicine.medicine_name,
                        'batch_number': medicine.batch_number,
                        'manufacturer': medicine.manufacturer,
                        'expiry_date': medicine.expiry_date,
                        'verification_status': medicine.verification_status,
                        'blockchain_verified': medicine.blockchain_verified,
                        'message': verification_result['message']
                    }
                    
                    # Check if expired
                    from datetime import date
                    if medicine.expiry_date and medicine.expiry_date < date.today():
                        response_data['warning'] = 'Medicine has expired'
                    
                    return Response(response_data, status=status.HTTP_201_CREATED)
                
                else:
                    return Response({
                        'verified': False,
                        'verification_status': 'unknown',
                        'message': 'Medicine not found in verification database',
                        'qr_code': qr_code
                    }, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({
                'error': f'Medicine verification failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class MedicineVerificationListView(generics.ListCreateAPIView):
    """
    List medicine verifications or create new verification
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Only admins and healthcare providers can see all verifications
        if self.request.user.user_type in ['admin', 'doctor', 'nurse']:
            return MedicineVerification.objects.all()
        return MedicineVerification.objects.none()
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return MedicineVerificationCreateSerializer
        return MedicineVerificationSerializer

class BlockchainTransactionListView(generics.ListAPIView):
    """
    List blockchain transactions
    """
    serializer_class = BlockchainTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Only admins can see all transactions
        if self.request.user.user_type == 'admin':
            return BlockchainTransaction.objects.all()
        return BlockchainTransaction.objects.none()

class PatientConsentListCreateView(generics.ListCreateAPIView):
    """
    List patient consent records or create new consent
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Patients can only see their own consent records
        if self.request.user.user_type == 'patient':
            return PatientConsentRecord.objects.filter(patient=self.request.user)
        # Healthcare providers can see consents for their patients
        elif self.request.user.user_type in ['doctor', 'nurse', 'admin']:
            return PatientConsentRecord.objects.all()
        return PatientConsentRecord.objects.none()
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ConsentCreateSerializer
        return PatientConsentRecordSerializer
    
    def perform_create(self, serializer):
        # Create consent hash
        import hashlib
        consent_data = f"{self.request.user.id}{serializer.validated_data['consent_type']}{serializer.validated_data['consent_text']}"
        consent_hash = hashlib.sha256(consent_data.encode()).hexdigest()
        
        serializer.save(
            patient=self.request.user,
            consent_hash=consent_hash
        )

class SmartContractListView(generics.ListAPIView):
    """
    List deployed smart contracts
    """
    serializer_class = SmartContractSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Only admins can see smart contract details
        if self.request.user.user_type == 'admin':
            return SmartContract.objects.filter(is_active=True)
        return SmartContract.objects.none()

class BlockchainStatusView(APIView):
    """
    Get blockchain network status
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        try:
            blockchain_service = BlockchainNetworkService()
            status_info = blockchain_service.get_network_status()
            
            serializer = BlockchainStatusSerializer(status_info)
            return Response(serializer.data)
            
        except Exception as e:
            return Response({
                'error': f'Failed to get blockchain status: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def check_transaction_status(request):
    """
    Check blockchain transaction status
    """
    serializer = TransactionStatusSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        tx_hash = serializer.validated_data['transaction_hash']
        
        blockchain_service = BlockchainNetworkService()
        tx_status = blockchain_service.get_transaction_status(tx_hash)
        
        return Response({
            'transaction_hash': tx_hash,
            'status': tx_status['status'],
            'block_number': tx_status.get('block_number'),
            'confirmations': tx_status.get('confirmations'),
            'gas_used': tx_status.get('gas_used'),
            'success': tx_status.get('success'),
            'error': tx_status.get('error')
        })
        
    except Exception as e:
        return Response({
            'error': f'Failed to check transaction status: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def revoke_consent(request, consent_id):
    """
    Revoke patient consent
    """
    try:
        if request.user.user_type == 'patient':
            consent = get_object_or_404(
                PatientConsentRecord,
                id=consent_id,
                patient=request.user
            )
        else:
            return Response({
                'error': 'Only patients can revoke their own consent'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Mark as revoked
        from django.utils import timezone
        consent.granted = False
        consent.revoked_at = timezone.now()
        consent.save()
        
        # TODO: Record revocation on blockchain
        
        serializer = PatientConsentRecordSerializer(consent)
        return Response({
            'message': 'Consent successfully revoked',
            'consent': serializer.data
        })
        
    except Exception as e:
        return Response({
            'error': f'Failed to revoke consent: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_medicine_batch_info(request, batch_number):
    """
    Get information about a medicine batch
    """
    try:
        medicines = MedicineVerification.objects.filter(
            batch_number=batch_number
        )
        
        if not medicines.exists():
            return Response({
                'found': False,
                'message': 'No medicines found for this batch number'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = MedicineVerificationSerializer(medicines, many=True)
        
        return Response({
            'found': True,
            'batch_number': batch_number,
            'medicines': serializer.data,
            'total_count': medicines.count()
        })
        
    except Exception as e:
        return Response({
            'error': f'Failed to get batch information: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
