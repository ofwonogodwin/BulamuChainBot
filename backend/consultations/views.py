from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, JSONParser
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import Consultation, ConsultationMessage, EmergencyAlert
from .serializers import (
    ConsultationSerializer, ConsultationCreateSerializer, 
    ConsultationListSerializer, ConsultationMessageSerializer,
    EmergencyAlertSerializer
)
from .services import AIConsultationService, EmergencyDetectionService

User = get_user_model()

class ConsultationListCreateView(generics.ListCreateAPIView):
    """
    List all consultations for the current user or create a new one
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return Consultation.objects.filter(patient=user, is_active=True)
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ConsultationCreateSerializer
        return ConsultationListSerializer
    
    def perform_create(self, serializer):
        consultation = serializer.save(patient=self.request.user)
        
        # Process AI consultation in background
        try:
            ai_service = AIConsultationService()
            ai_response = ai_service.process_consultation(consultation)
            
            consultation.ai_response = ai_response.get('response', '')
            consultation.severity_score = ai_response.get('severity_score')
            consultation.recommended_actions = ai_response.get('recommendations', '')
            consultation.save()
            
            # Store consultation on blockchain automatically for patients
            from blockchain.consultation_blockchain_service import ConsultationBlockchainService
            try:
                blockchain_service = ConsultationBlockchainService()
                blockchain_record = blockchain_service.store_consultation_on_blockchain(consultation)
                
                # Log successful blockchain storage
                print(f"✅ Consultation {consultation.id} stored on blockchain with hash {blockchain_record.consultation_hash}")
            except Exception as e:
                print(f"❌ Failed to store consultation {consultation.id} on blockchain: {str(e)}")
            
            # Check for emergency
            emergency_service = EmergencyDetectionService()
            if emergency_service.detect_emergency(consultation):
                consultation.emergency_detected = True
                consultation.save()
                emergency_service.create_emergency_alert(consultation)
                
        except Exception as e:
            # Log error but don't fail the consultation creation
            print(f"AI processing error: {str(e)}")

class ConsultationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a consultation
    """
    serializer_class = ConsultationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Consultation.objects.filter(patient=self.request.user)

class TextConsultationView(APIView):
    """
    Endpoint for text-based health consultations
    POST /api/consult
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            symptoms_text = request.data.get('symptoms', '')
            language = request.data.get('language', 'en')
            
            if not symptoms_text or len(symptoms_text.strip()) < 10:
                return Response({
                    'error': 'Please provide detailed symptoms (at least 10 characters)'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Create consultation record
            consultation = Consultation.objects.create(
                patient=request.user,
                consultation_type='text',
                language=language,
                symptoms_text=symptoms_text.strip()
            )
            
            # Process with AI
            ai_service = AIConsultationService()
            ai_response = ai_service.analyze_symptoms(
                symptoms_text, 
                language=language,
                user=request.user
            )
            
            # Update consultation with AI response
            consultation.ai_response = ai_response.get('response', '')
            consultation.severity_score = ai_response.get('severity_score', 5)
            consultation.recommended_actions = ai_response.get('recommendations', '')
            consultation.save()
            
            # Check for emergency
            emergency_service = EmergencyDetectionService()
            if emergency_service.detect_emergency_from_text(symptoms_text, ai_response):
                consultation.emergency_detected = True
                consultation.save()
                alert = emergency_service.create_emergency_alert(consultation, ai_response)
            
            # Create initial conversation messages
            ConsultationMessage.objects.create(
                consultation=consultation,
                message_type='user',
                content=symptoms_text
            )
            
            ConsultationMessage.objects.create(
                consultation=consultation,
                message_type='assistant',
                content=ai_response.get('response', '')
            )
            
            response_data = {
                'consultation_id': str(consultation.id),
                'ai_response': ai_response.get('response', ''),
                'severity_score': consultation.severity_score,
                'emergency_detected': consultation.emergency_detected,
                'recommendations': ai_response.get('recommendations', ''),
                'language': language,
                'created_at': consultation.created_at.isoformat()
            }
            
            return Response(response_data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'error': f'Consultation processing failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AudioConsultationView(APIView):
    """
    Endpoint for voice-based health consultations
    POST /api/consult-audio
    """
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser]
    
    def post(self, request):
        try:
            audio_file = request.FILES.get('audio_file')
            language = request.data.get('language', 'en')
            
            if not audio_file:
                return Response({
                    'error': 'Audio file is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validate audio file
            if audio_file.size > 5 * 1024 * 1024:  # 5MB limit
                return Response({
                    'error': 'Audio file too large (max 5MB)'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Create consultation record
            consultation = Consultation.objects.create(
                patient=request.user,
                consultation_type='voice',
                language=language,
                audio_file=audio_file,
                symptoms_text='[Audio consultation]'
            )
            
            # Process audio with AI
            ai_service = AIConsultationService()
            audio_response = ai_service.process_audio_consultation(
                audio_file,
                language=language,
                user=request.user
            )
            
            # Update consultation
            consultation.symptoms_text = audio_response.get('transcription', '[Audio consultation]')
            consultation.ai_response = audio_response.get('response', '')
            consultation.severity_score = audio_response.get('severity_score', 5)
            consultation.recommended_actions = audio_response.get('recommendations', '')
            consultation.save()
            
            # Check for emergency
            emergency_service = EmergencyDetectionService()
            if emergency_service.detect_emergency_from_text(
                audio_response.get('transcription', ''), 
                audio_response
            ):
                consultation.emergency_detected = True
                consultation.save()
                emergency_service.create_emergency_alert(consultation, audio_response)
            
            response_data = {
                'consultation_id': str(consultation.id),
                'transcription': audio_response.get('transcription', ''),
                'ai_response': audio_response.get('response', ''),
                'severity_score': consultation.severity_score,
                'emergency_detected': consultation.emergency_detected,
                'recommendations': audio_response.get('recommendations', ''),
                'language': language,
                'created_at': consultation.created_at.isoformat()
            }
            
            return Response(response_data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'error': f'Audio consultation processing failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ConsultationMessagesView(generics.ListCreateAPIView):
    """
    List messages for a consultation or add a new message
    """
    serializer_class = ConsultationMessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        consultation_id = self.kwargs['consultation_id']
        consultation = get_object_or_404(
            Consultation, 
            id=consultation_id, 
            patient=self.request.user
        )
        return ConsultationMessage.objects.filter(consultation=consultation)
    
    def perform_create(self, serializer):
        consultation_id = self.kwargs['consultation_id']
        consultation = get_object_or_404(
            Consultation,
            id=consultation_id,
            patient=self.request.user
        )
        
        message = serializer.save(
            consultation=consultation,
            message_type='user'
        )
        
        # Generate AI response for new user message
        try:
            ai_service = AIConsultationService()
            ai_response = ai_service.generate_followup_response(
                consultation,
                message.content
            )
            
            # Create AI response message
            ConsultationMessage.objects.create(
                consultation=consultation,
                message_type='assistant',
                content=ai_response.get('response', 'I understand. Could you provide more details?')
            )
            
        except Exception as e:
            # Create fallback response
            ConsultationMessage.objects.create(
                consultation=consultation,
                message_type='assistant',
                content='Thank you for the additional information. Please continue describing your symptoms.'
            )

class EmergencyAlertListView(generics.ListAPIView):
    """
    List emergency alerts for healthcare providers
    """
    serializer_class = EmergencyAlertSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Only doctors and admins can view emergency alerts
        if self.request.user.user_type in ['doctor', 'admin']:
            return EmergencyAlert.objects.filter(status='pending')
        return EmergencyAlert.objects.none()

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def acknowledge_emergency_alert(request, alert_id):
    """
    Acknowledge an emergency alert (doctors only)
    """
    if request.user.user_type not in ['doctor', 'admin']:
        return Response({
            'error': 'Only healthcare providers can acknowledge alerts'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        alert = EmergencyAlert.objects.get(id=alert_id)
        alert.status = 'acknowledged'
        alert.acknowledged_at = timezone.now()
        alert.save()
        
        serializer = EmergencyAlertSerializer(alert)
        return Response(serializer.data)
        
    except EmergencyAlert.DoesNotExist:
        return Response({
            'error': 'Emergency alert not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])  # Allow anonymous access for demo
def ai_chat(request):
    """
    Chat with AI using Gemini for health consultation
    """
    try:
        message = request.data.get('message', '')
        language = request.data.get('language', 'en')
        conversation_history = request.data.get('conversation_history', [])
        
        if not message.strip():
            return Response({
                'error': 'Message cannot be empty'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Initialize AI service
        ai_service = AIConsultationService()
        
        # Get AI response using Gemini
        ai_response = ai_service.chat_with_ai(
            message=message,
            language=language,
            conversation_history=conversation_history
        )
        
        return Response({
            'success': True,
            'response': ai_response.get('response', ''),
            'language': language,
            'timestamp': timezone.now().isoformat()
        })
        
    except Exception as e:
        # Fallback response
        fallback_responses = {
            'en': "I understand your concern. While I can provide general guidance, it's important to consult with a healthcare professional for proper diagnosis and treatment. Please describe your symptoms in more detail.",
            'lg': "Ntegeera ekirakubidde. Newankubadde nsobola okukuwa amagezi ag'okutandikira, kikulu olabe omusawo omukugu okufuna obujjanjabi obututuufu. Nnyonyola obubonero bwo mu bujjuvu.",
            'sw': "Ninaelewa wasiwasi wako. Ingawa ninaweza kutoa mwongozo wa jumla, ni muhimu kuona mtaalamu wa afya kwa uchunguzi na matibabu sahihi. Tafadhali elezea dalili zako kwa undani zaidi."
        }
        
        return Response({
            'success': True,
            'response': fallback_responses.get(language, fallback_responses['en']),
            'language': language,
            'timestamp': timezone.now().isoformat(),
            'note': 'Using fallback response due to service unavailability'
        })
