"""
Django views integration for LangChain Gemini 2.5 Flash Service
Provides API endpoints for both text and voice chat functionality
"""

import asyncio
import base64
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
import logging

from .langchain_gemini_service import HealthAssistantLangChain, get_ai_response, process_voice_message
from .models import Consultation, ConsultationMessage

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([AllowAny])  # Allow anonymous access for demo
def langchain_ai_chat(request):
    """
    Enhanced AI chat endpoint using LangChain and Gemini 2.5 Flash
    
    POST /api/langchain-chat/
    {
        "message": "I have a headache",
        "language": "en",
        "conversation_history": [...]
    }
    """
    try:
        message = request.data.get('message', '')
        language = request.data.get('language', 'en')
        user_id = str(request.user.id) if request.user.is_authenticated else None
        
        if not message.strip():
            return Response({
                'error': 'Message cannot be empty'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get AI response using async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            ai_response = loop.run_until_complete(
                get_ai_response(message, language, user_id)
            )
        finally:
            loop.close()
        
        return Response({
            'success': ai_response['success'],
            'response': ai_response['response'],
            'language': language,
            'model': ai_response.get('model', 'gemini-2.5-flash'),
            'conversation_length': ai_response.get('conversation_length', 0),
            'timestamp': ai_response['timestamp'],
            'fallback': ai_response.get('fallback', False)
        })
        
    except Exception as e:
        logger.error(f"LangChain chat error: {str(e)}")
        
        # Fallback response
        fallback_responses = {
            'en': "I understand your concern. Please consult with a healthcare professional for proper diagnosis and treatment.",
            'lg': "Ntegeera ekirakubidde. Kikulu olabe omusawo omukugu okufuna obujjanjabi obututuufu.",
            'sw': "Ninaelewa wasiwasi wako. Ni muhimu kuona mtaalamu wa afya kwa uchunguzi na matibabu sahihi."
        }
        
        language = request.data.get('language', 'en')
        return Response({
            'success': False,
            'response': fallback_responses.get(language, fallback_responses['en']),
            'language': language,
            'model': 'fallback',
            'timestamp': timezone.now().isoformat(),
            'error': 'Service temporarily unavailable'
        })

@api_view(['POST'])
@permission_classes([AllowAny])
def langchain_voice_chat(request):
    """
    Voice chat endpoint using LangChain and Gemini 2.5 Flash
    
    POST /api/langchain-voice-chat/
    Content-Type: multipart/form-data
    
    Form data:
        audio_file: Audio file (WAV, MP3, etc.)
        language: Language code (en, lg, sw)
    """
    try:
        audio_file = request.FILES.get('audio_file')
        language = request.data.get('language', 'en')
        user_id = str(request.user.id) if request.user.is_authenticated else None
        
        if not audio_file:
            return Response({
                'error': 'Audio file is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate audio file size (max 5MB)
        if audio_file.size > 5 * 1024 * 1024:
            return Response({
                'error': 'Audio file too large (max 5MB)'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Read audio data
        audio_data = audio_file.read()
        
        # Process voice message using async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            voice_response = loop.run_until_complete(
                process_voice_message(audio_data, language, user_id)
            )
        finally:
            loop.close()
        
        return Response({
            'success': voice_response['success'],
            'transcription': voice_response.get('transcription', ''),
            'ai_response_text': voice_response.get('ai_response_text', ''),
            'ai_response_audio': voice_response.get('ai_response_audio', {}),
            'language': language,
            'conversation_length': voice_response.get('conversation_length', 0),
            'error': voice_response.get('error')
        })
        
    except Exception as e:
        logger.error(f"LangChain voice chat error: {str(e)}")
        return Response({
            'success': False,
            'error': f'Voice processing failed: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LangChainChatSessionView(View):
    """
    Stateful chat session view that maintains conversation memory
    """
    
    def __init__(self):
        super().__init__()
        self.assistant = HealthAssistantLangChain()
    
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request):
        """Handle chat messages with conversation memory"""
        try:
            data = json.loads(request.body)
            message = data.get('message', '')
            language = data.get('language', 'en')
            action = data.get('action', 'chat')  # 'chat', 'clear', 'history'
            
            if action == 'clear':
                self.assistant.clear_conversation_memory()
                return JsonResponse({
                    'success': True,
                    'message': 'Conversation memory cleared'
                })
            
            elif action == 'history':
                history = self.assistant.get_conversation_history()
                return JsonResponse({
                    'success': True,
                    'conversation_history': history,
                    'length': len(history)
                })
            
            elif action == 'chat':
                if not message.strip():
                    return JsonResponse({
                        'error': 'Message cannot be empty'
                    }, status=400)
                
                # Get AI response with conversation memory
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                try:
                    response = loop.run_until_complete(
                        self.assistant.chat_with_ai(message, language)
                    )
                finally:
                    loop.close()
                
                return JsonResponse({
                    'success': response['success'],
                    'response': response['response'],
                    'language': language,
                    'conversation_length': response.get('conversation_length', 0),
                    'timestamp': response['timestamp']
                })
            
            else:
                return JsonResponse({
                    'error': 'Invalid action. Use: chat, clear, or history'
                }, status=400)
                
        except json.JSONDecodeError:
            return JsonResponse({
                'error': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            logger.error(f"Chat session error: {str(e)}")
            return JsonResponse({
                'error': f'Chat session failed: {str(e)}'
            }, status=500)

@api_view(['POST'])
@permission_classes([AllowAny])
def test_langchain_service(request):
    """
    Test endpoint for LangChain service functionality
    """
    try:
        assistant = HealthAssistantLangChain()
        
        # Test basic functionality
        test_results = {}
        
        # Test 1: Basic chat
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Test English
            en_response = loop.run_until_complete(
                assistant.chat_with_ai("Hello, I have a headache", "en")
            )
            test_results['english_chat'] = {
                'success': en_response['success'],
                'has_response': bool(en_response['response'])
            }
            
            # Test Luganda
            lg_response = loop.run_until_complete(
                assistant.chat_with_ai("Nnina omutwe", "lg")
            )
            test_results['luganda_chat'] = {
                'success': lg_response['success'],
                'has_response': bool(lg_response['response'])
            }
            
            # Test conversation memory
            followup = loop.run_until_complete(
                assistant.chat_with_ai("How long should I rest?", "en")
            )
            test_results['conversation_memory'] = {
                'success': followup['success'],
                'conversation_length': followup.get('conversation_length', 0)
            }
            
        finally:
            loop.close()
        
        # Test conversation history
        history = assistant.get_conversation_history()
        test_results['conversation_history'] = {
            'length': len(history),
            'has_messages': len(history) > 0
        }
        
        return Response({
            'success': True,
            'service_status': 'operational',
            'test_results': test_results,
            'timestamp': timezone.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"LangChain service test error: {str(e)}")
        return Response({
            'success': False,
            'service_status': 'error',
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# URL patterns for the new endpoints (add to urls.py)
"""
Add these to your consultations/urls.py:

from .langchain_views import (
    langchain_ai_chat, 
    langchain_voice_chat, 
    LangChainChatSessionView,
    test_langchain_service
)

urlpatterns = [
    # ... existing patterns ...
    
    # LangChain Gemini 2.5 Flash endpoints
    path('langchain-chat/', langchain_ai_chat, name='langchain_ai_chat'),
    path('langchain-voice-chat/', langchain_voice_chat, name='langchain_voice_chat'),
    path('langchain-session/', LangChainChatSessionView.as_view(), name='langchain_session'),
    path('test-langchain/', test_langchain_service, name='test_langchain'),
]
"""
