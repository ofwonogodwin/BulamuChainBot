"""
Intelligent Medical Chatbot with RAG and LangChain Integration
Combines conversational AI with medical knowledge retrieval
"""

import os
import logging
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import uuid

# LangChain imports
try:
    from langchain_community.llms import GoogleGenerativeAI
    from langchain.schema import HumanMessage, AIMessage
    from langchain.memory import ConversationBufferWindowMemory
    from langchain.callbacks import AsyncCallbackHandler
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    GoogleGenerativeAI = None
    HumanMessage = None
    AIMessage = None
    ConversationBufferWindowMemory = None
    AsyncCallbackHandler = None

# Local imports
from .rag_engine import RAGEngine
from .vector_store import VectorStoreManager
from .knowledge_base import MedicalKnowledgeBase

# Django imports
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

class ConversationCallback:
    """Callback handler for conversation logging and monitoring"""
    
    def __init__(self):
        self.logs = []
        # Only inherit from AsyncCallbackHandler if available
        if LANGCHAIN_AVAILABLE and AsyncCallbackHandler:
            self.__class__.__bases__ = (AsyncCallbackHandler,)
    
    async def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs) -> None:
        self.logs.append(f"LLM started with prompts: {len(prompts)}")
    
    async def on_llm_end(self, response, **kwargs) -> None:
        self.logs.append(f"LLM completed successfully")
    
    async def on_llm_error(self, error: Exception, **kwargs) -> None:
        self.logs.append(f"LLM error: {str(error)}")

class IntelligentMedicalChatbot:
    """
    Advanced medical chatbot with RAG capabilities
    Provides intelligent, context-aware medical conversations
    """
    
    def __init__(self):
        """Initialize the intelligent medical chatbot"""
        self.api_key = getattr(settings, 'GOOGLE_GEMINI_API_KEY', '')
        
        # Initialize LLM
        self.llm = self._initialize_llm()
        
        # Initialize RAG engine with LLM
        self.rag_engine = RAGEngine(llm=self.llm)
        
        # Initialize components
        self.knowledge_base = MedicalKnowledgeBase()
        self.vector_store = VectorStoreManager()
        
        # Conversation management
        self.active_conversations = {}
        self.conversation_timeout = 3600  # 1 hour
        
        # Callback handler
        self.callback_handler = ConversationCallback()
        
        # Supported languages
        self.supported_languages = ['english', 'luganda', 'swahili']
        
        # Chatbot personality and settings
        self.personality_config = {
            'empathy_level': 'high',
            'medical_accuracy': 'strict',
            'cultural_sensitivity': 'high',
            'emergency_alertness': 'maximum'
        }
        
        logger.info("Intelligent Medical Chatbot initialized successfully")
    
    def _initialize_llm(self):
        """Initialize Google Gemini LLM"""
        try:
            if not LANGCHAIN_AVAILABLE or not GoogleGenerativeAI:
                logger.warning("LangChain LLM not available. Chatbot will use fallback responses.")
                return None
                
            if self.api_key:
                return GoogleGenerativeAI(
                    model="gemini-2.5-flash",
                    google_api_key=self.api_key,
                    temperature=0.3,  # Conservative for medical advice
                    max_output_tokens=2000,
                    callbacks=[self.callback_handler] if self.callback_handler else []
                )
            else:
                logger.warning("No Gemini API key provided. Chatbot will use fallback responses.")
                return None
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}")
            return None
    
    async def start_conversation(
        self, 
        user_id: str, 
        language: str = "english",
        session_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Start a new conversation session
        
        Args:
            user_id: Unique identifier for the user
            language: Preferred language for conversation
            session_data: Optional session initialization data
            
        Returns:
            Conversation session information
        """
        conversation_id = str(uuid.uuid4())
        
        # Create conversation session
        session = {
            'conversation_id': conversation_id,
            'user_id': user_id,
            'language': language,
            'start_time': datetime.now().isoformat(),
            'message_count': 0,
            'last_activity': datetime.now().isoformat(),
            'context': session_data or {},
            'conversation_state': 'active',
            'emergency_flags': [],
            'medical_topics': [],
            'user_preferences': {
                'detail_level': 'standard',
                'include_local_context': True,
                'emergency_alerts': True
            }
        }
        
        # Store in memory and cache
        self.active_conversations[conversation_id] = session
        cache.set(f"conversation_{conversation_id}", session, timeout=self.conversation_timeout)
        
        # Generate welcome message
        welcome_message = await self._generate_welcome_message(language, session_data)
        
        return {
            'success': True,
            'conversation_id': conversation_id,
            'welcome_message': welcome_message,
            'session_info': {
                'language': language,
                'features_available': [
                    'medical_questions',
                    'symptom_analysis',
                    'emergency_guidance',
                    'preventive_care',
                    'medication_info',
                    'multilingual_support'
                ]
            }
        }
    
    async def send_message(
        self,
        conversation_id: str,
        message: str,
        message_type: str = "text",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Send a message in the conversation
        
        Args:
            conversation_id: Conversation session ID
            message: User message
            message_type: Type of message (text, voice, etc.)
            metadata: Additional message metadata
            
        Returns:
            Chatbot response with analysis
        """
        try:
            # Get conversation session
            session = await self._get_conversation_session(conversation_id)
            if not session:
                return {
                    'success': False,
                    'error': 'Conversation session not found or expired',
                    'action': 'restart_conversation'
                }
            
            # Update session activity
            session['last_activity'] = datetime.now().isoformat()
            session['message_count'] += 1
            
            # Pre-process message
            processed_message = await self._preprocess_message(message, session)
            
            # Check for emergency keywords
            emergency_check = self._check_emergency_intent(processed_message['text'])
            
            if emergency_check['is_emergency']:
                session['emergency_flags'].append({
                    'timestamp': datetime.now().isoformat(),
                    'keywords': emergency_check['keywords'],
                    'message': message
                })
                
                response = await self._handle_emergency_response(
                    processed_message['text'], 
                    session['language']
                )
            else:
                # Normal conversation flow
                response = await self._generate_intelligent_response(
                    message=processed_message['text'],
                    session=session,
                    message_metadata=metadata or {}
                )
            
            # Post-process response
            final_response = await self._postprocess_response(response, session)
            
            # Update conversation context
            await self._update_conversation_context(session, message, final_response)
            
            # Save session
            await self._save_conversation_session(session)
            
            return {
                'success': True,
                'response': final_response,
                'conversation_info': {
                    'message_count': session['message_count'],
                    'emergency_detected': emergency_check['is_emergency'],
                    'medical_topics': session.get('medical_topics', [])[-5:],  # Last 5 topics
                    'session_duration': self._calculate_session_duration(session)
                }
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {
                'success': False,
                'error': str(e),
                'fallback_response': "I apologize, but I encountered an error. Please try again or seek direct medical assistance if this is urgent."
            }
    
    async def _generate_welcome_message(
        self, 
        language: str, 
        session_data: Optional[Dict[str, Any]]
    ) -> str:
        """Generate personalized welcome message"""
        
        base_messages = {
            'english': (
                "Hello! I'm your AI medical assistant, here to help with your health questions. "
                "I can provide information about symptoms, conditions, preventive care, and emergency guidance. "
                "I'm knowledgeable about healthcare in Uganda and can communicate in multiple languages.\n\n"
                "How can I help you today? Feel free to ask about any health concerns you may have."
            ),
            'luganda': (
                "Oli otya! Nze omuyambi wo mu by'obulamu, ndi wano okukuyamba ku bibuuzo byo eby'obulamu. "
                "Nsobola okuwa obubaka ku bubonero bw'endwadde, embeera z'obulamu, n'okwekuuma. "
                "Mmanyi bingi ku by'obujjanjabi mu Uganda era nsobola okwogera mu nnimi nnyingi.\n\n"
                "Nkuyinza ntya okukuyamba leero? Buuza ku kye kyonna ekikwata ku bulamu bwo."
            ),
            'swahili': (
                "Hujambo! Mimi ni msaidizi wako wa kiafya, nipo hapa kukusaidia na maswali yako ya afya. "
                "Ninaweza kutoa habari kuhusu dalili, hali za afya, na miongozo ya dharura. "
                "Nina ujuzi wa huduma za afya nchini Uganda na ninaweza kuongea lugha nyingi.\n\n"
                "Ninawezaje kukusaidia leo? Huru kuuliza kuhusu wasiwasi wowote wa afya ulio nao."
            )
        }
        
        welcome = base_messages.get(language, base_messages['english'])
        
        # Add personalization if session data available
        if session_data and session_data.get('user_name'):
            name = session_data['user_name']
            if language == 'luganda':
                welcome = f"Oli otya {name}! " + welcome
            elif language == 'swahili':
                welcome = f"Hujambo {name}! " + welcome
            else:
                welcome = f"Hello {name}! " + welcome
        
        # Add current health context if available
        if session_data and session_data.get('health_concern'):
            concern = session_data['health_concern']
            if language == 'luganda':
                welcome += f"\n\nNlaba nti olina okuweraliikirivu ku {concern}. Nkuyinza okukuyamba okumanya ebisingawo."
            elif language == 'swahili':
                welcome += f"\n\nNaona una wasiwasi kuhusu {concern}. Ninaweza kukusaidia kupata maelezo zaidi."
            else:
                welcome += f"\n\nI see you have concerns about {concern}. I can help you learn more about this."
        
        return welcome
    
    async def _preprocess_message(self, message: str, session: Dict[str, Any]) -> Dict[str, Any]:
        """Preprocess incoming message"""
        return {
            'text': message.strip(),
            'language_detected': session['language'],  # Could implement language detection
            'tokens': len(message.split()),
            'preprocessed_at': datetime.now().isoformat()
        }
    
    def _check_emergency_intent(self, message: str) -> Dict[str, Any]:
        """Check if message indicates medical emergency"""
        emergency_keywords = [
            # English
            'emergency', 'urgent', 'chest pain', 'can\'t breathe', 'unconscious',
            'severe bleeding', 'heart attack', 'stroke', 'choking', 'seizure',
            'overdose', 'severe allergic reaction', 'suicide',
            
            # Luganda
            'mangu', 'amaanyi', 'omutima gukuba', 'ssisobola kussa mukka',
            'tafaayo', 'omusaayi oguyitiridde', 'okuzimba',
            
            # Swahili
            'dharura', 'haraka', 'maumivu ya kifua', 'siwezi kupumua',
            'amezimia', 'damu nyingi', 'shambulizi la moyo'
        ]
        
        message_lower = message.lower()
        detected_keywords = [kw for kw in emergency_keywords if kw in message_lower]
        
        return {
            'is_emergency': len(detected_keywords) > 0,
            'keywords': detected_keywords,
            'confidence': len(detected_keywords) / len(emergency_keywords.split())
        }
    
    async def _handle_emergency_response(self, message: str, language: str) -> Dict[str, Any]:
        """Handle emergency situations with immediate guidance"""
        
        emergency_responses = {
            'english': {
                'immediate_action': (
                    "🚨 MEDICAL EMERGENCY DETECTED 🚨\n\n"
                    "If this is a life-threatening emergency:\n"
                    "• Call emergency services IMMEDIATELY\n"
                    "• In Uganda: Call 999 or 112\n"
                    "• Go to the nearest hospital emergency room\n"
                    "• Don't delay seeking professional medical help\n\n"
                    "For urgent but non-life-threatening situations, contact your healthcare provider or visit the nearest clinic."
                ),
                'follow_up': "While waiting for emergency help, can you tell me more about the specific symptoms you're experiencing?"
            },
            'luganda': {
                'immediate_action': (
                    "🚨 EMBEERA Y'AMAANYI EY'OBUJJANJABI 🚨\n\n"
                    "Singa kino kya bulamu obw'amaanyi:\n"
                    "• Kuba amangu okubba simu 999 oba 112\n"
                    "• Genda mu ddwaliro ery'amangu\n"
                    "• Tolwa kufuna obuyambi obw'ekikugu\n\n"
                    "Okugeza nga si kya bulamu obw'amaanyi, kuba ku musawo wo oba genda mu ddukiro ery'okumpi."
                ),
                'follow_up': "Nga oluinda obuyambi bw'amangu, osobola okumbuulira ku bubonero bwe weetabye?"
            },
            'swahili': {
                'immediate_action': (
                    "🚨 DHARURA YA KIAFYA IMEGUNDULIKA 🚨\n\n"
                    "Ikiwa hii ni dharura ya maisha:\n"
                    "• Piga simu ya dharura MARA MOJA\n"
                    "• Nchini Uganda: Piga 999 au 112\n"
                    "• Nenda hospitali ya dharura ya karibu\n"
                    "• Usichelewe kutafuta msaada wa kitaalamu\n\n"
                    "Kwa hali za haraka zisizo za maisha, wasiliana na mtaalamu wako wa afya au tembelea kliniki ya karibu."
                ),
                'follow_up': "Unaposubiri msaada wa dharura, unaweza kuniambia zaidi kuhusu dalili maalum unazohisi?"
            }
        }
        
        response_data = emergency_responses.get(language, emergency_responses['english'])
        
        return {
            'answer': response_data['immediate_action'],
            'follow_up_question': response_data['follow_up'],
            'urgency': 'emergency',
            'action_required': 'seek_immediate_help',
            'emergency_numbers': {
                'uganda_emergency': ['999', '112'],
                'police': '999',
                'medical': '999'
            }
        }
    
    async def _generate_intelligent_response(
        self,
        message: str,
        session: Dict[str, Any],
        message_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate intelligent response using RAG engine"""
        
        # Use RAG engine for intelligent response
        rag_response = await self.rag_engine.ask_question(
            question=message,
            conversation_id=session['conversation_id'],
            language=session['language'],
            include_sources=True
        )
        
        # Enhance with conversational context
        if rag_response['success']:
            # Add personality and empathy
            enhanced_response = await self._add_conversational_personality(
                response=rag_response['answer'],
                session=session,
                question_type=rag_response.get('question_type', 'general')
            )
            
            rag_response['answer'] = enhanced_response
            
            # Track medical topics
            if rag_response.get('metadata', {}).get('categories'):
                session.setdefault('medical_topics', []).extend(
                    rag_response['metadata']['categories']
                )
        
        return rag_response
    
    async def _add_conversational_personality(
        self,
        response: str,
        session: Dict[str, Any],
        question_type: str
    ) -> str:
        """Add empathy and personality to responses"""
        
        # Empathetic openings based on question type
        empathy_openings = {
            'symptoms': {
                'english': "I understand you're concerned about these symptoms. ",
                'luganda': "Ntegeera nti weraliikirira ku bubonero buno. ",
                'swahili': "Naelewa una wasiwasi kuhusu dalili hizi. "
            },
            'treatment': {
                'english': "I can help you understand treatment options. ",
                'luganda': "Nsobola okukuyamba okumanya engeri ez'okujjanjaba. ",
                'swahili': "Ninaweza kukusaidia kuelewa chaguo za matibabu. "
            },
            'prevention': {
                'english': "Prevention is always important for good health. ",
                'luganda': "Okwekuuma kya mugaso nnyo mu bulamu obulungi. ",
                'swahili': "Kujikinga ni muhimu kwa afya njema. "
            }
        }
        
        language = session.get('language', 'english')
        
        # Add appropriate opening
        if question_type in empathy_openings and language in empathy_openings[question_type]:
            opening = empathy_openings[question_type][language]
            response = opening + response
        
        # Add encouraging closing for certain types
        if question_type in ['symptoms', 'treatment']:
            encouragements = {
                'english': "\n\nRemember, I'm here to help with any other questions you might have.",
                'luganda': "\n\nJjukira nti ndi wano okukuyamba mu bibuuzo ebirala byonna by'oyinza okubeera nabyo.",
                'swahili': "\n\nKumbuka, nipo hapa kukusaidia na maswali mengine yoyote unayoweza kuwa nayo."
            }
            
            if language in encouragements:
                response += encouragements[language]
        
        return response
    
    async def _postprocess_response(
        self,
        response: Dict[str, Any],
        session: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Post-process response for better user experience"""
        
        # Add conversation continuity
        response['conversation_flow'] = {
            'follow_up_suggestions': await self._generate_follow_up_suggestions(
                response, session
            ),
            'related_topics': await self._get_related_topics(response, session),
            'next_steps': await self._suggest_next_steps(response, session)
        }
        
        # Add user preference adaptations
        user_prefs = session.get('user_preferences', {})
        
        if user_prefs.get('detail_level') == 'detailed':
            response['additional_info'] = await self._get_additional_details(response)
        
        if user_prefs.get('include_local_context'):
            response['local_context'] = await self._get_ugandan_context(response)
        
        return response
    
    async def _generate_follow_up_suggestions(
        self,
        response: Dict[str, Any],
        session: Dict[str, Any]
    ) -> List[str]:
        """Generate relevant follow-up questions"""
        
        question_type = response.get('question_type', 'general')
        language = session.get('language', 'english')
        
        suggestions = {
            'symptoms': {
                'english': [
                    "Would you like to know about treatment options?",
                    "Should I explain when to seek medical attention?",
                    "Are you interested in prevention strategies?"
                ],
                'luganda': [
                    "Oyagala okumanya ku ngeri ez'okujjanjaba?",
                    "Nkutegeeze ddi lw'oneetaaga okufuna obujjanjabi?",
                    "Oyagala okumanya ku ngeri ez'okwekuuma?"
                ],
                'swahili': [
                    "Ungependa kujua kuhusu chaguo za matibabu?",
                    "Je, nieleeze ni lini utakapohitaji kutafuta huduma za kiafya?",
                    "Una hamu ya kujua mikakati ya kujikinga?"
                ]
            },
            'treatment': {
                'english': [
                    "Do you have questions about side effects?",
                    "Would you like information about follow-up care?",
                    "Should I explain how to monitor progress?"
                ]
            }
        }
        
        return suggestions.get(question_type, {}).get(language, [])[:3]
    
    async def _get_related_topics(
        self,
        response: Dict[str, Any],
        session: Dict[str, Any]
    ) -> List[str]:
        """Get related medical topics"""
        
        categories = response.get('metadata', {}).get('categories', [])
        related_topics = []
        
        if 'infectious_diseases' in categories:
            related_topics.extend(['Prevention', 'Vaccination', 'Hygiene'])
        
        if 'maternal_child_health' in categories:
            related_topics.extend(['Prenatal care', 'Child nutrition', 'Immunization'])
        
        if 'non_communicable_diseases' in categories:
            related_topics.extend(['Lifestyle changes', 'Diet', 'Exercise'])
        
        return related_topics[:3]
    
    async def _suggest_next_steps(
        self,
        response: Dict[str, Any],
        session: Dict[str, Any]
    ) -> List[str]:
        """Suggest actionable next steps"""
        
        urgency = response.get('urgency', 'normal')
        
        if urgency == 'high':
            return ["Seek immediate medical attention", "Monitor symptoms closely"]
        elif urgency == 'normal':
            return ["Schedule regular checkup", "Maintain healthy lifestyle", "Monitor any changes"]
        else:
            return ["Continue healthy practices", "Stay informed about health topics"]
    
    async def _get_additional_details(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Get additional detailed information"""
        return {
            'detailed_explanation': "Additional medical context available upon request",
            'scientific_background': "Research-based information available",
            'statistical_data': "Prevalence and outcome data available"
        }
    
    async def _get_ugandan_context(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Get Uganda-specific health context"""
        return {
            'local_prevalence': "Information about condition prevalence in Uganda",
            'healthcare_access': "Local healthcare facility recommendations",
            'cultural_considerations': "Cultural health practices and integration",
            'government_programs': "Available government health programs"
        }
    
    async def _update_conversation_context(
        self,
        session: Dict[str, Any],
        user_message: str,
        bot_response: Dict[str, Any]
    ):
        """Update conversation context and memory"""
        
        # Add to conversation history
        if 'conversation_history' not in session:
            session['conversation_history'] = []
        
        session['conversation_history'].append({
            'timestamp': datetime.now().isoformat(),
            'user_message': user_message,
            'bot_response': bot_response.get('answer', ''),
            'question_type': bot_response.get('question_type', 'general'),
            'urgency': bot_response.get('urgency', 'normal')
        })
        
        # Keep only last 20 exchanges
        if len(session['conversation_history']) > 20:
            session['conversation_history'] = session['conversation_history'][-20:]
        
        # Update medical topics
        if bot_response.get('metadata', {}).get('categories'):
            categories = bot_response['metadata']['categories']
            session.setdefault('medical_topics', []).extend(categories)
            # Keep unique topics only
            session['medical_topics'] = list(set(session['medical_topics']))[-10:]
    
    async def _get_conversation_session(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Get conversation session from memory or cache"""
        
        # Try memory first
        if conversation_id in self.active_conversations:
            return self.active_conversations[conversation_id]
        
        # Try cache
        cached_session = cache.get(f"conversation_{conversation_id}")
        if cached_session:
            self.active_conversations[conversation_id] = cached_session
            return cached_session
        
        return None
    
    async def _save_conversation_session(self, session: Dict[str, Any]):
        """Save conversation session to memory and cache"""
        conversation_id = session['conversation_id']
        
        # Update memory
        self.active_conversations[conversation_id] = session
        
        # Update cache
        cache.set(
            f"conversation_{conversation_id}",
            session,
            timeout=self.conversation_timeout
        )
    
    def _calculate_session_duration(self, session: Dict[str, Any]) -> str:
        """Calculate session duration"""
        start_time = datetime.fromisoformat(session['start_time'])
        duration = datetime.now() - start_time
        
        total_minutes = int(duration.total_seconds() / 60)
        hours = total_minutes // 60
        minutes = total_minutes % 60
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
    
    async def end_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """End conversation session"""
        session = await self._get_conversation_session(conversation_id)
        
        if not session:
            return {'success': False, 'error': 'Conversation not found'}
        
        # Generate summary
        summary = {
            'conversation_id': conversation_id,
            'duration': self._calculate_session_duration(session),
            'message_count': session.get('message_count', 0),
            'medical_topics_discussed': session.get('medical_topics', []),
            'emergency_flags': len(session.get('emergency_flags', [])),
            'end_time': datetime.now().isoformat()
        }
        
        # Clean up
        if conversation_id in self.active_conversations:
            del self.active_conversations[conversation_id]
        
        cache.delete(f"conversation_{conversation_id}")
        
        return {
            'success': True,
            'summary': summary,
            'farewell_message': await self._generate_farewell_message(session)
        }
    
    async def _generate_farewell_message(self, session: Dict[str, Any]) -> str:
        """Generate farewell message"""
        language = session.get('language', 'english')
        
        farewells = {
            'english': "Thank you for using the medical assistant. Take care of your health, and don't hesitate to reach out if you have more questions. Stay healthy!",
            'luganda': "Webale okukozesa omuyambi w'obujjanjabi. Kuuma obulamu bwo, era tolwaana kutuukirivu bwe waba n'ebibuuzo ebirala. Beera bulungi!",
            'swahili': "Asante kwa kutumia msaidizi wa kiafya. Jali afya yako, na usisite kuwasiliana ikiwa una maswali mengine. Uwe na afya njema!"
        }
        
        return farewells.get(language, farewells['english'])
    
    def get_chatbot_statistics(self) -> Dict[str, Any]:
        """Get comprehensive chatbot performance statistics"""
        
        active_sessions = len(self.active_conversations)
        
        # Collect metrics from active conversations
        total_messages = sum(
            session.get('message_count', 0) 
            for session in self.active_conversations.values()
        )
        
        emergency_count = sum(
            len(session.get('emergency_flags', []))
            for session in self.active_conversations.values()
        )
        
        return {
            'active_conversations': active_sessions,
            'total_messages_processed': total_messages,
            'emergency_situations_handled': emergency_count,
            'supported_languages': self.supported_languages,
            'rag_engine_metrics': self.rag_engine.get_performance_metrics(),
            'system_status': {
                'llm_available': self.llm is not None,
                'knowledge_base_loaded': True,
                'vector_store_active': self.vector_store.get_store_statistics()['chroma_available']
            },
            'callback_logs': self.callback_handler.logs[-10:]  # Last 10 logs
        }
