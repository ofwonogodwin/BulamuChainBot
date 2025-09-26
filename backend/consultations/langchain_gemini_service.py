"""
Enhanced AI Health Assistant Service using LangChain and Google Gemini 2.5 Flash
Handles both text and voice chat interactions for BulamuChainBot
"""

import os
import logging
import asyncio
from typing import Dict, List, Optional, Union, Any
from datetime import datetime
import speech_recognition as sr
import pyttsx3
from gtts import gTTS
import tempfile
import io
import base64

# LangChain imports
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from langchain.memory import ConversationBufferWindowMemory
from langchain.callbacks import StreamingStdOutCallbackHandler
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import ConversationChain

# Django imports
from django.conf import settings
from django.contrib.auth import get_user_model
from .models import Consultation, ConsultationMessage

# Initialize logger
logger = logging.getLogger(__name__)
User = get_user_model()

class HealthAssistantLangChain:
    """
    Advanced AI Health Assistant using LangChain with Gemini 2.5 Flash
    Supports both text and voice interactions with conversation memory
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the LangChain Health Assistant
        
        Args:
            api_key: Google Gemini API key (optional, will use settings if not provided)
        """
        self.api_key = api_key or getattr(settings, 'GOOGLE_GEMINI_API_KEY', '')
        
        if not self.api_key:
            logger.warning("No Google Gemini API key found. Service will use fallback responses.")
            self.llm = None
        else:
            # Initialize Gemini 2.5 Flash with LangChain
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                google_api_key=self.api_key,
                temperature=0.3,
                max_tokens=500,
                streaming=True,
                callbacks=[StreamingStdOutCallbackHandler()]
            )
        
        # Initialize conversation history manually (simpler approach)
        self.conversation_history = []
        
        # Initialize voice components
        self.speech_recognizer = sr.Recognizer()
        self.tts_engine = None
        self._init_tts_engine()
        
        # Health system prompt
        self.system_prompt = self._create_health_system_prompt()
        
    def _init_tts_engine(self):
        """Initialize text-to-speech engine"""
        try:
            self.tts_engine = pyttsx3.init()
            # Set properties for better voice
            voices = self.tts_engine.getProperty('voices')
            if voices:
                # Try to use a female voice for healthcare
                for voice in voices:
                    if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                        self.tts_engine.setProperty('voice', voice.id)
                        break
            
            self.tts_engine.setProperty('rate', 150)  # Speaking rate
            self.tts_engine.setProperty('volume', 0.9)  # Volume level
        except Exception as e:
            logger.error(f"Failed to initialize TTS engine: {e}")
            self.tts_engine = None
    
    def _create_health_system_prompt(self) -> str:
        """Create comprehensive health assistant system prompt"""
        return """You are BulamuChainBot, an AI health assistant specifically designed for rural and underserved communities in Uganda and East Africa. 

Your expertise includes:
- General health guidance and first aid
- Common tropical diseases (malaria, typhoid, dengue)
- Maternal and child health
- Preventive care and hygiene
- Traditional and modern medicine integration
- Cultural sensitivity for African healthcare practices

Your personality:
- Empathetic and caring
- Culturally sensitive to Ugandan/East African contexts
- Professional yet approachable
- Always emphasize the importance of professional medical care
- Provide practical, actionable advice

Guidelines:
- Never diagnose specific medical conditions
- Always recommend seeing healthcare professionals for serious symptoms
- Provide general health information and first aid guidance
- Consider local healthcare infrastructure and resources
- Be aware of language preferences (English, Luganda, Swahili)
- Mention local health resources like Village Health Teams (VHTs)
- Consider economic constraints when giving advice

Emergency symptoms to immediately refer to healthcare:
- Difficulty breathing or chest pain
- Severe bleeding
- High fever with stiff neck
- Severe abdominal pain
- Signs of dehydration in children
- Unconsciousness or seizures
- Severe allergic reactions

Always end responses with encouraging words and remind users that professional medical care is important for proper diagnosis and treatment.
"""
    
    def _add_to_history(self, message: str, is_user: bool = True):
        """Add message to conversation history"""
        self.conversation_history.append({
            'role': 'user' if is_user else 'assistant',
            'content': message,
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep only last 20 messages to manage memory
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]
    
    async def chat_with_ai(
        self, 
        message: str, 
        language: str = 'en',
        user_id: Optional[str] = None,
        conversation_context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Main chat method using LangChain and Gemini 2.5 Flash
        
        Args:
            message: User's message/question
            language: Language code ('en', 'lg', 'sw')
            user_id: Optional user ID for personalization
            conversation_context: Optional context from previous conversations
            
        Returns:
            Dict with response, success status, and metadata
        """
        try:
            if not self.llm:
                return await self._fallback_response(message, language)
            
            # Add user message to history
            self._add_to_history(message, is_user=True)
            
            # Create messages for LangChain
            messages = [SystemMessage(content=self.system_prompt)]
            
            # Add conversation history
            for msg in self.conversation_history[-10:]:  # Last 10 messages
                if msg['role'] == 'user':
                    messages.append(HumanMessage(content=msg['content']))
                else:
                    messages.append(AIMessage(content=msg['content']))
            
            # Add language instruction
            language_instruction = self._get_language_instruction(language)
            final_message = f"{language_instruction}\n\nUser message: {message}"
            messages.append(HumanMessage(content=final_message))
            
            # Get AI response using LangChain
            response = await asyncio.get_event_loop().run_in_executor(
                None, 
                self.llm.invoke,
                messages
            )
            
            # Extract response content
            response_text = response.content if hasattr(response, 'content') else str(response)
            
            # Add AI response to history
            self._add_to_history(response_text, is_user=False)
            
            # Process and enhance response
            processed_response = self._process_ai_response(response_text, language)
            
            return {
                'response': processed_response,
                'success': True,
                'language': language,
                'timestamp': datetime.now().isoformat(),
                'model': 'gemini-2.5-flash',
                'conversation_length': len(self.conversation_history)
            }
            
        except Exception as e:
            logger.error(f"LangChain AI chat error: {str(e)}")
            return await self._fallback_response(message, language)
    
    def _get_language_instruction(self, language: str) -> str:
        """Get language-specific instructions"""
        language_instructions = {
            'en': "Please respond in clear, simple English suitable for rural communities.",
            'lg': "Please respond in Luganda language. Use simple, everyday Luganda words that rural communities can understand.",
            'sw': "Please respond in Swahili language. Use simple, clear Swahili suitable for East African communities."
        }
        return language_instructions.get(language, language_instructions['en'])
    
    def _process_ai_response(self, response: str, language: str) -> str:
        """Process and enhance AI response with local context"""
        # Add local health resources information
        if language == 'en':
            footer = "\n\nFor urgent care, visit your nearest health center or contact a Village Health Team (VHT) member."
        elif language == 'lg':
            footer = "\n\nSinga kyetaaga obujjanjabi obw'amangu, kyalira ku ddwaliro oba kutuukiriza omuntu w'ekibinja ky'ebyobulamu (VHT)."
        elif language == 'sw':
            footer = "\n\nKwa huduma ya haraka, tembelea kituo cha afya au wasiliana na mwanachama wa Timu ya Afya ya Kijiji (VHT)."
        else:
            footer = "\n\nFor urgent care, visit your nearest health center."
        
        # Add footer if response doesn't already mention health centers
        if "health center" not in response.lower() and "ddwaliro" not in response.lower():
            response += footer
            
        return response
    
    async def voice_to_text(self, audio_data: bytes, language: str = 'en') -> Dict[str, Any]:
        """
        Convert voice input to text using speech recognition
        
        Args:
            audio_data: Raw audio bytes
            language: Language code for recognition
            
        Returns:
            Dict with transcribed text and success status
        """
        try:
            # Create temporary audio file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name
            
            # Recognize speech
            with sr.AudioFile(temp_file_path) as source:
                audio = self.speech_recognizer.record(source)
            
            # Language mapping for speech recognition
            lang_map = {
                'en': 'en-US',
                'lg': 'en-US',  # Fallback to English for Luganda
                'sw': 'sw-KE'   # Swahili (Kenya)
            }
            
            recognition_language = lang_map.get(language, 'en-US')
            
            # Transcribe using Google Speech Recognition
            text = self.speech_recognizer.recognize_google(
                audio, 
                language=recognition_language
            )
            
            # Cleanup temp file
            os.unlink(temp_file_path)
            
            return {
                'text': text,
                'success': True,
                'language_detected': language,
                'confidence': 0.9  # Placeholder confidence
            }
            
        except sr.UnknownValueError:
            return {
                'text': '',
                'success': False,
                'error': 'Could not understand audio',
                'language_detected': language
            }
        except sr.RequestError as e:
            logger.error(f"Speech recognition request error: {e}")
            return {
                'text': '',
                'success': False,
                'error': 'Speech recognition service unavailable',
                'language_detected': language
            }
        except Exception as e:
            logger.error(f"Voice to text error: {e}")
            return {
                'text': '',
                'success': False,
                'error': str(e),
                'language_detected': language
            }
    
    def text_to_voice(self, text: str, language: str = 'en') -> Dict[str, Any]:
        """
        Convert text response to voice audio
        
        Args:
            text: Text to convert to speech
            language: Language for TTS
            
        Returns:
            Dict with audio data and metadata
        """
        try:
            # Language mapping for gTTS
            tts_lang_map = {
                'en': 'en',
                'lg': 'en',  # Fallback to English for Luganda
                'sw': 'sw'
            }
            
            tts_language = tts_lang_map.get(language, 'en')
            
            # Generate speech using Google TTS
            tts = gTTS(text=text, lang=tts_language, slow=False)
            
            # Create audio buffer
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            
            # Convert to base64 for easy transmission
            audio_b64 = base64.b64encode(audio_buffer.getvalue()).decode()
            
            return {
                'audio_data': audio_b64,
                'audio_format': 'mp3',
                'success': True,
                'language': language,
                'text_length': len(text)
            }
            
        except Exception as e:
            logger.error(f"Text to voice error: {e}")
            return {
                'audio_data': None,
                'success': False,
                'error': str(e),
                'language': language
            }
    
    async def voice_chat(
        self, 
        audio_data: bytes, 
        language: str = 'en',
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Complete voice chat pipeline: voice -> text -> AI -> voice
        
        Args:
            audio_data: Input audio bytes
            language: Language code
            user_id: Optional user ID
            
        Returns:
            Dict with both text and voice responses
        """
        try:
            # Step 1: Convert voice to text
            speech_result = await self.voice_to_text(audio_data, language)
            
            if not speech_result['success']:
                error_message = "Sorry, I couldn't understand your voice message. Please try again."
                if language == 'lg':
                    error_message = "Nkusonyiwa, sisobola kutegeera obubaka bwo. Gezaako nate."
                elif language == 'sw':
                    error_message = "Samahani, sikuelewi ujumbe wako. Jaribu tena."
                
                return {
                    'transcription': '',
                    'ai_response_text': error_message,
                    'ai_response_audio': self.text_to_voice(error_message, language),
                    'success': False,
                    'error': speech_result.get('error', 'Voice recognition failed')
                }
            
            transcribed_text = speech_result['text']
            
            # Step 2: Get AI response
            ai_response = await self.chat_with_ai(
                transcribed_text, 
                language=language, 
                user_id=user_id
            )
            
            # Step 3: Convert AI response to voice
            voice_response = self.text_to_voice(ai_response['response'], language)
            
            return {
                'transcription': transcribed_text,
                'ai_response_text': ai_response['response'],
                'ai_response_audio': voice_response,
                'success': True,
                'language': language,
                'conversation_length': ai_response.get('conversation_length', 0)
            }
            
        except Exception as e:
            logger.error(f"Voice chat pipeline error: {e}")
            error_message = "I'm having technical difficulties. Please try again later."
            return {
                'transcription': '',
                'ai_response_text': error_message,
                'ai_response_audio': self.text_to_voice(error_message, language),
                'success': False,
                'error': str(e)
            }
    
    async def _fallback_response(self, message: str, language: str) -> Dict[str, Any]:
        """Enhanced fallback response system"""
        message_lower = message.lower()
        
        # Health condition responses
        health_responses = {
            'en': {
                'headache': "For headaches, try resting in a quiet, dark room. Stay hydrated and consider applying a cold compress. If headaches persist or worsen, please visit a healthcare provider.",
                'fever': "For fever, rest and drink plenty of fluids. Use paracetamol if available. Seek medical care if fever is above 38.5°C (101°F) or persists for more than 2 days.",
                'cough': "For persistent cough, stay hydrated and use honey if available. See a doctor if cough lasts more than 2 weeks, has blood, or comes with breathing difficulties.",
                'stomach': "For stomach issues, eat bland foods and stay hydrated with small sips of water. Avoid dairy and fatty foods. Seek immediate care for severe pain or blood in stool.",
                'malaria': "Malaria prevention: Use mosquito nets, eliminate standing water, wear long sleeves at dusk. Symptoms include fever, chills, headache. Seek immediate testing and treatment.",
                'default': "I understand your health concern. While I can provide general guidance, please consult with a healthcare professional for proper diagnosis and treatment."
            },
            'lg': {
                'headache': "Omutwe bwe gukubagira, wewummule mu kisenge ekitalimu oluyoogaano. Nywa amazzi mangi era teeka ekintu ekinnyogovu ku mutwe. Singa omutwe gukyeyongera okukubagira, laba omusawo.",
                'fever': "Omusujja bwe guba guliko, wewummule era nywa amazzi mangi. Kozesa panadol singa guliko. Laba omusawo singa omusujja gusukka 38.5°C oba gukyeyongera okumala ennaku 2.",
                'cough': "Okukoola okw'emirembe egiwanvu, nywa amazzi mangi era kozesa omubisi gw'enjuki. Laba omusawo singa okukoola kukyeyongera okumala wiiki 2 oba kuliko omusai.",
                'stomach': "Olubuto bwe lukubagira, lya emmere entono era nywa amazzi matono matono. Weekweke amata n'emmere ezimu masavu. Laba omusawo amangu singa olina obulumi obungi.",
                'malaria': "Okuziyiza omusujja gw'ensiri: kozesa akatimba k'ensiri, gyawo amazzi agayimiridde, bambala engoye empanvu akawungeezi. Obubonero: omusujja, okukankana, omutwe okukuba.",
                'default': "Ntegeera ebikulwazizza ku bulamu bwo. Newankubadde nsobola okukuwa amagezi ag'okutandikira, kikulu olabe omusawo okufuna obujjanjabi obututuufu."
            }
        }
        
        responses = health_responses.get(language, health_responses['en'])
        
        # Find relevant response
        for condition, response in responses.items():
            if condition != 'default' and condition in message_lower:
                return {
                    'response': response,
                    'success': False,
                    'fallback': True,
                    'language': language,
                    'timestamp': datetime.now().isoformat()
                }
        
        return {
            'response': responses['default'],
            'success': False,
            'fallback': True,
            'language': language,
            'timestamp': datetime.now().isoformat()
        }
    
    def clear_conversation_memory(self):
        """Clear conversation memory for new session"""
        self.conversation_history = []
    
    def get_conversation_history(self) -> List[Dict]:
        """Get current conversation history"""
        return self.conversation_history.copy()

# Async helper functions for Django views
async def get_ai_response(message: str, language: str = 'en', user_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Helper function for getting AI responses in Django views
    """
    assistant = HealthAssistantLangChain()
    return await assistant.chat_with_ai(message, language, user_id)

async def process_voice_message(audio_data: bytes, language: str = 'en', user_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Helper function for processing voice messages in Django views  
    """
    assistant = HealthAssistantLangChain()
    return await assistant.voice_chat(audio_data, language, user_id)

# Example usage and testing
if __name__ == "__main__":
    async def test_assistant():
        """Test the AI assistant functionality"""
        assistant = HealthAssistantLangChain()
        
        # Test text chat
        print("Testing text chat...")
        response = await assistant.chat_with_ai("I have a headache and fever", "en")
        print(f"Response: {response['response']}")
        print(f"Success: {response['success']}")
        
        # Test conversation memory
        print("\nTesting follow-up question...")
        followup = await assistant.chat_with_ai("How long should I rest?", "en")
        print(f"Follow-up response: {followup['response']}")
        
        # Test Luganda
        print("\nTesting Luganda response...")
        lg_response = await assistant.chat_with_ai("Nnina omutwe era nkukoowa", "lg")
        print(f"Luganda response: {lg_response['response']}")
        
        print(f"\nConversation history: {len(assistant.get_conversation_history())} messages")
    
    # Run test
    asyncio.run(test_assistant())
