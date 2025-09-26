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


# Consultation Blockchain Endpoints

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_patient_consultation_records(request):
    """
    Get all blockchain records for patient's consultations
    """
    try:
        from .consultation_blockchain_service import ConsultationBlockchainService
        from .models import ConsultationBlockchainRecord
        
        blockchain_service = ConsultationBlockchainService()
        
        if request.user.user_type == 'patient':
            # Patients can see their own records
            consultation_records = blockchain_service.get_patient_consultation_records(request.user)
        elif request.user.user_type in ['doctor', 'nurse']:
            # Healthcare providers can see records they have access to
            consultation_records = blockchain_service.get_provider_accessible_records(request.user)
        else:
            return Response({
                'error': 'Access denied'
            }, status=status.HTTP_403_FORBIDDEN)
        
        records_data = []
        for record in consultation_records:
            # Log access
            blockchain_service.log_consultation_access(record, request.user, request)
            
            record_data = {
                'id': str(record.id),
                'consultation_id': str(record.consultation.id),
                'consultation_hash': record.consultation_hash,
                'patient': record.patient.username if request.user.user_type != 'patient' else 'You',
                'symptoms_preview': record.consultation.symptoms_text[:100] + '...' if len(record.consultation.symptoms_text) > 100 else record.consultation.symptoms_text,
                'severity_score': record.consultation.severity_score,
                'emergency_detected': record.consultation.emergency_detected,
                'stored_on_blockchain': record.stored_on_blockchain,
                'encrypted': record.encrypted,
                'created_at': record.created_at,
                'language': record.consultation.language
            }
            records_data.append(record_data)
        
        return Response({
            'consultation_records': records_data,
            'total_count': len(records_data)
        })
        
    except Exception as e:
        return Response({
            'error': f'Failed to get consultation records: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def grant_provider_access(request):
    """
    Grant healthcare provider access to patient's consultation record
    """
    try:
        from .consultation_blockchain_service import ConsultationBlockchainService
        from .models import ConsultationBlockchainRecord
        
        # Only patients can grant access to their consultations
        if request.user.user_type != 'patient':
            return Response({
                'error': 'Only patients can grant access to their consultations'
            }, status=status.HTTP_403_FORBIDDEN)
        
        consultation_record_id = request.data.get('consultation_record_id')
        provider_username = request.data.get('provider_username')
        access_level = request.data.get('access_level', 'read_only')
        purpose = request.data.get('purpose', '')
        expires_in_days = int(request.data.get('expires_in_days', 30))
        
        if not consultation_record_id or not provider_username:
            return Response({
                'error': 'consultation_record_id and provider_username are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get consultation record
        try:
            consultation_record = ConsultationBlockchainRecord.objects.get(
                id=consultation_record_id,
                patient=request.user
            )
        except ConsultationBlockchainRecord.DoesNotExist:
            return Response({
                'error': 'Consultation record not found or not owned by you'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get healthcare provider
        try:
            healthcare_provider = User.objects.get(
                username=provider_username,
                user_type__in=['doctor', 'nurse']
            )
        except User.DoesNotExist:
            return Response({
                'error': 'Healthcare provider not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Grant access
        blockchain_service = ConsultationBlockchainService()
        access_record = blockchain_service.grant_provider_access(
            patient=request.user,
            healthcare_provider=healthcare_provider,
            consultation_record=consultation_record,
            access_level=access_level,
            purpose=purpose,
            expires_in_days=expires_in_days
        )
        
        return Response({
            'message': 'Access granted successfully',
            'access_record_id': str(access_record.id),
            'provider': healthcare_provider.username,
            'access_level': access_record.access_level,
            'expires_at': access_record.expires_at,
            'blockchain_hash': access_record.access_grant_hash
        })
        
    except Exception as e:
        return Response({
            'error': f'Failed to grant provider access: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_consultation_details(request, consultation_record_id):
    """
    Get detailed consultation information from blockchain record
    """
    try:
        from .consultation_blockchain_service import ConsultationBlockchainService
        from .models import ConsultationBlockchainRecord
        
        blockchain_service = ConsultationBlockchainService()
        
        # Get consultation record
        try:
            consultation_record = ConsultationBlockchainRecord.objects.get(id=consultation_record_id)
        except ConsultationBlockchainRecord.DoesNotExist:
            return Response({
                'error': 'Consultation record not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check access permissions
        if request.user.user_type == 'patient':
            # Patients can only access their own consultations
            if consultation_record.patient != request.user:
                return Response({
                    'error': 'Access denied'
                }, status=status.HTTP_403_FORBIDDEN)
            provider_access = None
        elif request.user.user_type in ['doctor', 'nurse']:
            # Healthcare providers need granted access
            access_check = blockchain_service.verify_provider_access(request.user, consultation_record)
            if not access_check['has_access']:
                return Response({
                    'error': 'Access denied. No valid access grant found.',
                    'message': access_check['message']
                }, status=status.HTTP_403_FORBIDDEN)
            provider_access = access_check['access_record']
        else:
            return Response({
                'error': 'Access denied'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Log access
        blockchain_service.log_consultation_access(consultation_record, request.user, request, provider_access)
        
        # Verify data integrity
        integrity_check = blockchain_service.verify_consultation_integrity(consultation_record)
        
        # Return consultation details
        consultation = consultation_record.consultation
        consultation_data = {
            'id': str(consultation.id),
            'patient_username': consultation.patient.username,
            'symptoms': consultation.symptoms_text,
            'ai_response': consultation.ai_response,
            'severity_score': consultation.severity_score,
            'emergency_detected': consultation.emergency_detected,
            'recommended_actions': consultation.recommended_actions,
            'language': consultation.language,
            'consultation_type': consultation.consultation_type,
            'created_at': consultation.created_at,
            'updated_at': consultation.updated_at,
            'blockchain_hash': consultation_record.consultation_hash,
            'stored_on_blockchain': consultation_record.stored_on_blockchain,
            'encrypted': consultation_record.encrypted,
            'integrity_verified': integrity_check['verified'],
            'integrity_message': integrity_check['message']
        }
        
        return Response(consultation_data)
        
    except Exception as e:
        return Response({
            'error': f'Failed to get consultation details: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def revoke_provider_access(request):
    """
    Revoke healthcare provider's access to consultation record
    """
    try:
        from .consultation_blockchain_service import ConsultationBlockchainService
        from .models import ConsultationBlockchainRecord
        
        # Only patients can revoke access to their consultations
        if request.user.user_type != 'patient':
            return Response({
                'error': 'Only patients can revoke access to their consultations'
            }, status=status.HTTP_403_FORBIDDEN)
        
        consultation_record_id = request.data.get('consultation_record_id')
        provider_username = request.data.get('provider_username')
        
        if not consultation_record_id or not provider_username:
            return Response({
                'error': 'consultation_record_id and provider_username are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get consultation record
        try:
            consultation_record = ConsultationBlockchainRecord.objects.get(
                id=consultation_record_id,
                patient=request.user
            )
        except ConsultationBlockchainRecord.DoesNotExist:
            return Response({
                'error': 'Consultation record not found or not owned by you'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get healthcare provider
        try:
            healthcare_provider = User.objects.get(username=provider_username)
        except User.DoesNotExist:
            return Response({
                'error': 'Healthcare provider not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Revoke access
        blockchain_service = ConsultationBlockchainService()
        success = blockchain_service.revoke_provider_access(
            patient=request.user,
            healthcare_provider=healthcare_provider,
            consultation_record=consultation_record
        )
        
        if success:
            return Response({
                'message': f'Access revoked for {provider_username}'
            })
        else:
            return Response({
                'error': 'No active access found to revoke'
            }, status=status.HTTP_404_NOT_FOUND)
        
    except Exception as e:
        return Response({
            'error': f'Failed to revoke provider access: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
