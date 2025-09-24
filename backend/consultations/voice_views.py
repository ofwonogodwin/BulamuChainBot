"""
Voice API Views for BulamuChainBot
Handles voice-related API endpoints
"""

import logging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.files.base import ContentFile
from .voice_services import voice_processing_service, voice_consultation_service
from .models import Consultation
from .serializers import ConsultationMessageSerializer

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def speech_to_text(request):
    """
    Convert uploaded audio to text
    
    POST /api/consultations/speech-to-text/
    Body: multipart/form-data with 'audio' file and optional 'language'
    """
    try:
        # Get audio file from request
        audio_file = request.FILES.get('audio')
        if not audio_file:
            return Response({
                'success': False,
                'message': 'No audio file provided'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get language parameter
        language = request.data.get('language', 'en')
        
        # Validate audio file
        is_valid, error_message = voice_processing_service.validate_audio_format(audio_file)
        if not is_valid:
            return Response({
                'success': False,
                'message': error_message
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Process audio file
        result = voice_processing_service.process_audio_file(audio_file, language)
        
        return Response(result, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error in speech-to-text API: {e}")
        return Response({
            'success': False,
            'message': f'Error processing speech-to-text: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def text_to_speech(request):
    """
    Convert text to speech audio
    
    POST /api/consultations/text-to-speech/
    Body: JSON with 'text', optional 'language' and 'slow'
    """
    try:
        # Get parameters from request
        text = request.data.get('text')
        if not text:
            return Response({
                'success': False,
                'message': 'No text provided'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        language = request.data.get('language', 'en')
        slow = request.data.get('slow', False)
        
        # Convert text to speech
        result = voice_processing_service.text_to_speech(text, language, slow)
        
        return Response(result, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error in text-to-speech API: {e}")
        return Response({
            'success': False,
            'message': f'Error processing text-to-speech: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class VoiceConsultationView(APIView):
    """
    Handle voice-based consultations
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, consultation_id):
        """
        Process voice input for a consultation
        
        POST /api/consultations/{consultation_id}/voice/
        Body: multipart/form-data with 'audio' file and optional 'language'
        """
        try:
            # Check if consultation exists and user has access
            try:
                consultation = Consultation.objects.get(
                    id=consultation_id,
                    patient=request.user
                )
            except Consultation.DoesNotExist:
                return Response({
                    'success': False,
                    'message': 'Consultation not found or access denied'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Check consultation status
            if consultation.status == 'ended':
                return Response({
                    'success': False,
                    'message': 'Consultation has ended'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get audio file from request
            audio_file = request.FILES.get('audio')
            if not audio_file:
                return Response({
                    'success': False,
                    'message': 'No audio file provided'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get language parameter
            language = request.data.get('language', consultation.language or 'en')
            
            # Validate audio file
            is_valid, error_message = voice_processing_service.validate_audio_format(audio_file)
            if not is_valid:
                return Response({
                    'success': False,
                    'message': error_message
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Read audio data
            audio_data = audio_file.read()
            
            # Process voice consultation
            result = voice_consultation_service.process_voice_consultation(
                audio_data=audio_data,
                consultation_id=str(consultation_id),
                language=language
            )
            
            # If successful, save the message to database
            if result.get('success'):
                # Create patient message
                patient_message = consultation.messages.create(
                    sender=request.user,
                    message=result['transcribed_text'],
                    message_type='patient'
                )
                
                # Create AI response message
                if result.get('ai_response'):
                    ai_message = consultation.messages.create(
                        sender=None,  # AI message
                        message=result['ai_response'],
                        message_type='ai'
                    )
                
                # Update consultation status if needed
                consultation.status = 'active'
                consultation.save()
            
            return Response(result, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in voice consultation API: {e}")
            return Response({
                'success': False,
                'message': f'Error processing voice consultation: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def supported_languages(request):
    """
    Get supported languages for voice processing
    
    GET /api/consultations/voice/languages/
    """
    try:
        result = voice_processing_service.get_supported_languages()
        return Response(result, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error getting supported languages: {e}")
        return Response({
            'success': False,
            'message': f'Error getting supported languages: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class VoiceMessageView(APIView):
    """
    Convert existing text messages to speech
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, message_id):
        """
        Convert a consultation message to speech
        
        POST /api/consultations/messages/{message_id}/to-speech/
        Body: JSON with optional 'language' and 'slow'
        """
        try:
            # Get message and check access
            from .models import ConsultationMessage
            
            try:
                message = ConsultationMessage.objects.get(id=message_id)
                consultation = message.consultation
                
                # Check if user has access to this consultation
                if consultation.patient != request.user and not request.user.is_staff:
                    return Response({
                        'success': False,
                        'message': 'Access denied'
                    }, status=status.HTTP_403_FORBIDDEN)
                    
            except ConsultationMessage.DoesNotExist:
                return Response({
                    'success': False,
                    'message': 'Message not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Get parameters
            language = request.data.get('language', consultation.language or 'en')
            slow = request.data.get('slow', False)
            
            # Convert message to speech
            result = voice_processing_service.text_to_speech(
                text=message.message,
                language=language,
                slow=slow
            )
            
            # Add message metadata
            if result.get('success'):
                result['message_id'] = message_id
                result['message_type'] = message.message_type
                result['sender'] = message.sender.get_full_name() if message.sender else 'AI Assistant'
            
            return Response(result, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error converting message to speech: {e}")
            return Response({
                'success': False,
                'message': f'Error converting message to speech: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
