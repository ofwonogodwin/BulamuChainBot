from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, JSONParser
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.http import Http404

from .models import MedicalRecord, PatientProfile, RecordAccessLog
from .serializers import (
    MedicalRecordSerializer, MedicalRecordCreateSerializer,
    MedicalRecordListSerializer, PatientProfileSerializer,
    RecordAccessLogSerializer, BlockchainStoreSerializer,
    MedicalRecordRetrieveSerializer
)
from .services import BlockchainService, RecordEncryptionService

User = get_user_model()

class PatientProfileView(generics.RetrieveUpdateAPIView):
    """
    Retrieve or update patient profile
    """
    serializer_class = PatientProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        try:
            return PatientProfile.objects.get(user=self.request.user)
        except PatientProfile.DoesNotExist:
            return PatientProfile.objects.create(user=self.request.user)

class MedicalRecordListCreateView(generics.ListCreateAPIView):
    """
    List medical records for current user or create new record
    """
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, JSONParser]
    
    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'patient':
            return MedicalRecord.objects.filter(patient=user, is_active=True)
        elif user.user_type in ['doctor', 'nurse', 'admin']:
            # Healthcare providers can see records they have access to
            return MedicalRecord.objects.filter(is_active=True)
        return MedicalRecord.objects.none()
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return MedicalRecordCreateSerializer
        return MedicalRecordListSerializer
    
    def perform_create(self, serializer):
        # For patients, set themselves as the patient
        if self.request.user.user_type == 'patient':
            patient = self.request.user
        else:
            # Healthcare providers should specify patient
            patient = self.request.user  # This should be modified to accept patient parameter
        
        record = serializer.save(patient=patient)
        
        # Log the record creation
        self._log_record_access(record, 'create')
        
        # Optionally store on blockchain if consent given
        if self.request.data.get('store_on_blockchain'):
            try:
                blockchain_service = BlockchainService()
                blockchain_service.store_medical_record(record)
            except Exception as e:
                # Don't fail record creation if blockchain fails
                pass
    
    def _log_record_access(self, record, access_type):
        """Log access to medical record"""
        RecordAccessLog.objects.create(
            medical_record=record,
            accessed_by=self.request.user,
            access_type=access_type,
            ip_address=self.get_client_ip(),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )
    
    def get_client_ip(self):
        """Get client IP address"""
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return self.request.META.get('REMOTE_ADDR')

class MedicalRecordDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or soft-delete a medical record
    """
    serializer_class = MedicalRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, JSONParser]
    
    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'patient':
            return MedicalRecord.objects.filter(patient=user, is_active=True)
        elif user.user_type in ['doctor', 'nurse', 'admin']:
            return MedicalRecord.objects.filter(is_active=True)
        return MedicalRecord.objects.none()
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Log access
        RecordAccessLog.objects.create(
            medical_record=instance,
            accessed_by=request.user,
            access_type='view',
            ip_address=self._get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def perform_destroy(self, instance):
        # Soft delete
        instance.is_active = False
        instance.save()
        
        # Log deletion
        RecordAccessLog.objects.create(
            medical_record=instance,
            accessed_by=self.request.user,
            access_type='delete',
            ip_address=self._get_client_ip(self.request)
        )
    
    def _get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')

class StoreMedicalRecordView(APIView):
    """
    Store medical record hash on blockchain
    POST /api/records/store
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = BlockchainStoreSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            record_id = serializer.validated_data['record_id']
            
            # Get the medical record
            if request.user.user_type == 'patient':
                record = get_object_or_404(
                    MedicalRecord, 
                    id=record_id, 
                    patient=request.user,
                    is_active=True
                )
            else:
                record = get_object_or_404(
                    MedicalRecord,
                    id=record_id,
                    is_active=True
                )
            
            # Check if already on blockchain
            if record.is_on_blockchain:
                return Response({
                    'error': 'Record is already stored on blockchain',
                    'transaction_hash': record.blockchain_tx_hash
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Store on blockchain
            blockchain_service = BlockchainService()
            tx_hash = blockchain_service.store_medical_record(record)
            
            # Update record
            record.blockchain_tx_hash = tx_hash
            record.is_on_blockchain = True
            record.save()
            
            # Log blockchain storage
            RecordAccessLog.objects.create(
                medical_record=record,
                accessed_by=request.user,
                access_type='blockchain_store',
                ip_address=self._get_client_ip(request)
            )
            
            return Response({
                'success': True,
                'record_id': str(record.id),
                'transaction_hash': tx_hash,
                'record_hash': record.record_hash,
                'message': 'Medical record successfully stored on blockchain'
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'error': f'Failed to store record on blockchain: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')

class RetrieveMedicalRecordView(APIView):
    """
    Retrieve medical record by ID with access logging
    GET /api/records/{id}
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, record_id):
        try:
            # Get the medical record
            if request.user.user_type == 'patient':
                record = get_object_or_404(
                    MedicalRecord,
                    id=record_id,
                    patient=request.user,
                    is_active=True
                )
            elif request.user.user_type in ['doctor', 'nurse', 'admin']:
                record = get_object_or_404(
                    MedicalRecord,
                    id=record_id,
                    is_active=True
                )
            else:
                return Response({
                    'error': 'Unauthorized access'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Log access
            RecordAccessLog.objects.create(
                medical_record=record,
                accessed_by=request.user,
                access_type='view',
                ip_address=self._get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            # Serialize and return record
            serializer = MedicalRecordSerializer(record)
            return Response(serializer.data)
            
        except Http404:
            return Response({
                'error': 'Medical record not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'error': f'Failed to retrieve record: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')

class RecordAccessLogView(generics.ListAPIView):
    """
    View access logs for medical records
    """
    serializer_class = RecordAccessLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        record_id = self.kwargs.get('record_id')
        
        if user.user_type == 'patient':
            # Patients can only see logs for their own records
            return RecordAccessLog.objects.filter(
                medical_record__id=record_id,
                medical_record__patient=user
            )
        elif user.user_type in ['doctor', 'admin']:
            # Healthcare providers can see logs for records they have access to
            return RecordAccessLog.objects.filter(
                medical_record__id=record_id
            )
        return RecordAccessLog.objects.none()

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def verify_blockchain_record(request, record_id):
    """
    Verify medical record integrity using blockchain
    """
    try:
        # Get the medical record
        if request.user.user_type == 'patient':
            record = get_object_or_404(
                MedicalRecord,
                id=record_id,
                patient=request.user,
                is_active=True
            )
        else:
            record = get_object_or_404(
                MedicalRecord,
                id=record_id,
                is_active=True
            )
        
        if not record.is_on_blockchain:
            return Response({
                'verified': False,
                'message': 'Record is not stored on blockchain'
            })
        
        # Verify with blockchain
        blockchain_service = BlockchainService()
        verification_result = blockchain_service.verify_medical_record(record)
        
        return Response({
            'verified': verification_result['verified'],
            'record_hash': record.record_hash,
            'blockchain_hash': verification_result.get('blockchain_hash'),
            'transaction_hash': record.blockchain_tx_hash,
            'message': verification_result.get('message', '')
        })
        
    except Exception as e:
        return Response({
            'error': f'Verification failed: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
