"""
Django views for AI Engine integration
Provides API endpoints for intelligent medical chatbot with RAG capabilities
"""

import json
import logging
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from django.core.cache import cache
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

# Local imports
try:
    from ai_engine.intelligent_chatbot import IntelligentMedicalChatbot
    from ai_engine.rag_engine import RAGEngine
    from ai_engine.knowledge_base import MedicalKnowledgeBase
    CHATBOT_AVAILABLE = True
except ImportError as e:
    CHATBOT_AVAILABLE = False
    logging.warning(f"AI Engine not available: {e}")

logger = logging.getLogger(__name__)

# Initialize chatbot (singleton pattern)
_chatbot_instance = None

def run_async(coro):
    """Helper function to run async functions in sync context"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(coro)

def get_chatbot_instance():
    """Get or create chatbot instance"""
    global _chatbot_instance
    
    if not CHATBOT_AVAILABLE:
        return None
    
    if _chatbot_instance is None:
        try:
            _chatbot_instance = IntelligentMedicalChatbot()
            logger.info("Intelligent Medical Chatbot initialized")
        except Exception as e:
            logger.error(f"Failed to initialize chatbot: {e}")
            return None
    
    return _chatbot_instance

@api_view(['POST'])
@permission_classes([AllowAny])
def intelligent_chat(request):
    """Handle intelligent chat messages"""
    try:
        # Parse request
        data = request.data
        message = data.get('message', '').strip()
        conversation_id = data.get('conversation_id')
        language = data.get('language', 'english')
        message_type = data.get('message_type', 'text')
        user_id = data.get('user_id', 'anonymous')
        
        if not message:
            return Response({
                'success': False,
                'error': 'Message is required'
            }, status=400)
        
        # Get chatbot instance
        chatbot = get_chatbot_instance()
        if not chatbot:
            return _fallback_response(message, language)
        
        # Start new conversation if needed
        if not conversation_id:
            session_result = run_async(chatbot.start_conversation(
                user_id=user_id,
                language=language,
                session_data=data.get('session_data')
            ))
            
            if not session_result['success']:
                return Response({
                    'success': False,
                    'error': 'Failed to start conversation'
                }, status=500)
            
            conversation_id = session_result['conversation_id']
            
            # Return welcome message
            return Response({
                'success': True,
                'conversation_id': conversation_id,
                'response': {
                    'answer': session_result['welcome_message'],
                    'question_type': 'welcome',
                    'urgency': 'normal'
                },
                'session_info': session_result['session_info']
            })
        
        # Send message to chatbot
        response = run_async(chatbot.send_message(
            conversation_id=conversation_id,
            message=message,
            message_type=message_type,
            metadata=data.get('metadata', {})
        ))
        
        if response['success']:
            return Response({
                'success': True,
                'conversation_id': conversation_id,
                'response': response['response'],
                'conversation_info': response['conversation_info']
            })
        else:
            return Response({
                'success': False,
                'error': response.get('error', 'Unknown error'),
                'fallback_response': response.get('fallback_response')
            }, status=500)
    
    except Exception as e:
        logger.error(f"Error in intelligent chat: {e}")
        return Response({
            'success': False,
            'error': str(e),
            'fallback': 'I apologize, but I encountered an error. Please try again.'
        }, status=500)

def _fallback_response(message: str, language: str) -> Response:
    """Provide fallback response when chatbot is unavailable"""
    
    fallback_messages = {
        'english': (
            "I'm currently experiencing technical difficulties with the advanced AI system. "
            "For medical questions, please consult with a healthcare provider directly. "
            "If this is an emergency, please call 999 or go to the nearest hospital immediately."
        ),
        'luganda': (
            "Ndi mu buzibu bw'ekikugu mu sisitemu y'amagezi. "
            "Ku bibuuzo by'obujjanjabi, nsaba oggende ku musawo. "
            "Bwe kiba kya maangu, kuba 999 oba genda mu ddwaliro ery'okumpi amangu."
        ),
        'swahili': (
            "Nina shida za kiufundi na mfumo wa akili bandia. "
            "Kwa maswali ya afya, tafadhali wasiliana na mtaalamu wa afya moja kwa moja. "
            "Ikiwa ni dharura, piga 999 au nenda hospitali ya karibu haraka."
        )
    }
    
    return Response({
        'success': False,
        'error': 'AI system temporarily unavailable',
        'fallback_response': fallback_messages.get(language, fallback_messages['english']),
        'system_status': 'degraded'
    })

@api_view(['POST'])
@permission_classes([AllowAny])
def start_intelligent_conversation(request):
    """Start a new intelligent conversation session"""
    try:
        data = request.data
        user_id = data.get('user_id', 'anonymous')
        language = data.get('language', 'english')
        session_data = data.get('session_data', {})
        
        chatbot = get_chatbot_instance()
        if not chatbot:
            return Response({
                'success': False,
                'error': 'Intelligent chatbot not available'
            }, status=503)
        
        result = run_async(chatbot.start_conversation(
            user_id=user_id,
            language=language,
            session_data=session_data
        ))
        
        return Response(result)
    
    except Exception as e:
        logger.error(f"Error starting intelligent conversation: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)

@api_view(['POST'])
@permission_classes([AllowAny])
def end_intelligent_conversation(request):
    """End an intelligent conversation session"""
    try:
        data = request.data
        conversation_id = data.get('conversation_id')
        
        if not conversation_id:
            return Response({
                'success': False,
                'error': 'Conversation ID is required'
            }, status=400)
        
        chatbot = get_chatbot_instance()
        if not chatbot:
            return Response({
                'success': False,
                'error': 'Intelligent chatbot not available'
            }, status=503)
        
        result = run_async(chatbot.end_conversation(conversation_id))
        return Response(result)
    
    except Exception as e:
        logger.error(f"Error ending conversation: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)

@api_view(['POST'])
@permission_classes([AllowAny])
def intelligent_voice_chat(request):
    """Handle voice chat with intelligent processing"""
    try:
        data = request.data
        conversation_id = data.get('conversation_id')
        audio_data = data.get('audio_data')  # Base64 encoded audio
        language = data.get('language', 'english')
        
        if not conversation_id:
            return Response({
                'success': False,
                'error': 'Conversation ID is required'
            }, status=400)
        
        chatbot = get_chatbot_instance()
        if not chatbot:
            return Response({
                'success': False,
                'error': 'Intelligent chatbot not available'
            }, status=503)
        
        # Process voice input (would need speech-to-text integration)
        # For now, assume we have text from voice
        message = data.get('transcribed_text', data.get('message', ''))
        
        if not message:
            return Response({
                'success': False,
                'error': 'Voice transcription failed or message missing'
            }, status=400)
        
        # Send to chatbot
        response = run_async(chatbot.send_message(
            conversation_id=conversation_id,
            message=message,
            message_type='voice',
            metadata={'audio_provided': True}
        ))
        
        # Add voice synthesis info to response
        if response['success']:
            response['voice_synthesis'] = {
                'text_to_speak': response['response']['answer'],
                'language': language,
                'voice_speed': 'normal'
            }
        
        return Response(response)
    
    except Exception as e:
        logger.error(f"Error in voice chat: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def rag_search(request):
    """Search medical knowledge using RAG"""
    try:
        query = request.GET.get('query', '').strip()
        language = request.GET.get('language', 'english')
        
        if not query:
            return Response({
                'success': False,
                'error': 'Search query is required'
            }, status=400)
        
        chatbot = get_chatbot_instance()
        if not chatbot:
            return Response({
                'success': False,
                'error': 'RAG system not available'
            }, status=503)
        
        # Use RAG engine directly for search
        rag_engine = chatbot.rag_engine
        result = run_async(rag_engine.ask_question(
            question=query,
            language=language,
            include_sources=True
        ))
        
        return Response({
            'success': True,
            'query': query,
            'result': result,
            'search_type': 'rag_enhanced'
        })
    
    except Exception as e:
        logger.error(f"Error in RAG search: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def medical_knowledge_search(request):
    """Search medical knowledge base directly"""
    try:
        query = request.GET.get('query', '').strip()
        language = request.GET.get('language', 'english')
        category = request.GET.get('category', '')
        
        if not query:
            return Response({
                'success': False,
                'error': 'Search query is required'
            }, status=400)
        
        # Initialize knowledge base
        try:
            knowledge_base = MedicalKnowledgeBase()
        except Exception as e:
            return Response({
                'success': False,
                'error': 'Medical knowledge base not available'
            }, status=503)
        
        # Search knowledge base
        results = knowledge_base.search_knowledge(query, language)
        
        # Filter by category if provided
        if category and category in results:
            results = {category: results[category]}
        
        return Response({
            'success': True,
            'query': query,
            'language': language,
            'category_filter': category,
            'results': results,
            'search_type': 'knowledge_base'
        })
    
    except Exception as e:
        logger.error(f"Error in knowledge search: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)

@api_view(['POST'])
@permission_classes([AllowAny])
def symptom_analysis(request):
    """Analyze symptoms using medical knowledge base"""
    try:
        data = request.data
        symptoms = data.get('symptoms', [])
        language = data.get('language', 'english')
        
        if not symptoms or not isinstance(symptoms, list):
            return Response({
                'success': False,
                'error': 'Symptoms list is required'
            }, status=400)
        
        # Initialize knowledge base
        try:
            knowledge_base = MedicalKnowledgeBase()
        except Exception as e:
            return Response({
                'success': False,
                'error': 'Medical knowledge base not available'
            }, status=503)
        
        # Analyze symptoms
        analysis = knowledge_base.get_symptoms_analysis(symptoms)
        
        return Response({
            'success': True,
            'symptoms': symptoms,
            'language': language,
            'analysis': analysis,
            'disclaimer': (
                'This analysis is for informational purposes only. '
                'Please consult a healthcare provider for proper diagnosis and treatment.'
            )
        })
    
    except Exception as e:
        logger.error(f"Error in symptom analysis: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def chatbot_status(request):
    """Get comprehensive chatbot system status"""
    try:
        chatbot = get_chatbot_instance()
        
        if not chatbot:
            return Response({
                'success': False,
                'system_available': False,
                'error': 'Chatbot system not available'
            })
        
        stats = chatbot.get_chatbot_statistics()
        
        return Response({
            'success': True,
            'system_available': True,
            'statistics': stats,
            'capabilities': {
                'rag_enabled': True,
                'multilingual_support': True,
                'voice_chat': True,
                'emergency_detection': True,
                'medical_knowledge_base': True,
                'conversation_memory': True
            }
        })
    
    except Exception as e:
        logger.error(f"Error getting chatbot status: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)

@api_view(['POST'])
@permission_classes([AllowAny])
def add_medical_knowledge(request):
    """Add new medical knowledge to the system"""
    try:
        data = request.data
        knowledge_data = data.get('knowledge_data')
        
        if not knowledge_data:
            return Response({
                'success': False,
                'error': 'Knowledge data is required'
            }, status=400)
        
        chatbot = get_chatbot_instance()
        if not chatbot:
            return Response({
                'success': False,
                'error': 'Chatbot system not available'
            }, status=503)
        
        # Add knowledge to RAG engine
        success = run_async(chatbot.rag_engine.add_new_knowledge(knowledge_data))
        
        return Response({
            'success': success,
            'message': 'Knowledge added successfully' if success else 'Failed to add knowledge'
        })
    
    except Exception as e:
        logger.error(f"Error adding medical knowledge: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)

# Legacy compatibility view for existing frontend
@api_view(['POST'])
@permission_classes([AllowAny])
def legacy_chat(request):
    """Handle legacy chat requests"""
    try:
        data = request.data
        message = data.get('message', '').strip()
        language = data.get('language', 'english')
        
        if not message:
            return Response({
                'success': False,
                'error': 'Message is required'
            }, status=400)
        
        chatbot = get_chatbot_instance()
        if not chatbot:
            # Fallback to simple responses
            return Response({
                'success': True,
                'response': _get_simple_fallback(message, language),
                'enhanced': False
            })
        
        # Start a temporary conversation
        session_result = run_async(chatbot.start_conversation(
            user_id='legacy_user',
            language=language
        ))
        
        if not session_result['success']:
            return Response({
                'success': True,
                'response': _get_simple_fallback(message, language),
                'enhanced': False
            })
        
        conversation_id = session_result['conversation_id']
        
        # Send message
        response = run_async(chatbot.send_message(
            conversation_id=conversation_id,
            message=message
        ))
        
        # End conversation immediately for legacy compatibility
        run_async(chatbot.end_conversation(conversation_id))
        
        if response['success']:
            return Response({
                'success': True,
                'response': response['response']['answer'],
                'enhanced': True,
                'question_type': response['response'].get('question_type'),
                'urgency': response['response'].get('urgency')
            })
        else:
            return Response({
                'success': True,
                'response': response.get('fallback_response', _get_simple_fallback(message, language)),
                'enhanced': False
            })
    
    except Exception as e:
        logger.error(f"Error in legacy chat: {e}")
        return Response({
            'success': True,
            'response': _get_simple_fallback(message or '', 'english'),
            'enhanced': False,
            'error': str(e)
        })

def _get_simple_fallback(message: str, language: str) -> str:
    """Simple fallback responses"""
    
    fallbacks = {
        'english': "I understand you have a medical question. Please consult with a healthcare provider for proper medical advice.",
        'luganda': "Ntegeera nti olina ekibuuzo ky'obujjanjabi. Nsaba ogende ku musawo afune obujjanjabi obulungi.",
        'swahili': "Naelewa una swali la kiafya. Tafadhali wasiliana na mtaalamu wa afya kwa ushauri sahihi wa kiafya."
    }
    
    return fallbacks.get(language, fallbacks['english'])
