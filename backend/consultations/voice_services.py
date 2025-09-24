"""
Voice Processing Services for BulamuChainBot
Handles speech-to-text and text-to-speech functionality
"""

import os
import io
import base64
import tempfile
import logging
from typing import Dict, Any, Optional, Tuple
import speech_recognition as sr
from gtts import gTTS
from pydub import AudioSegment
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

logger = logging.getLogger(__name__)

class VoiceProcessingService:
    """Service for processing voice input and generating voice output"""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.supported_languages = {
            'en': {'code': 'en-US', 'name': 'English', 'gtts_code': 'en'},
            'lg': {'code': 'en-US', 'name': 'Luganda', 'gtts_code': 'en'},  # Using English TTS for Luganda
        }
        
        # Configure recognizer settings
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        self.recognizer.phrase_threshold = 0.3

    def speech_to_text(self, audio_data: bytes, language: str = 'en') -> Dict[str, Any]:
        """
        Convert speech audio to text
        
        Args:
            audio_data: Binary audio data
            language: Language code ('en' or 'lg')
            
        Returns:
            Dict containing transcribed text and confidence
        """
        try:
            # Get language configuration
            lang_config = self.supported_languages.get(language, self.supported_languages['en'])
            
            # Create temporary file for audio processing
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio:
                temp_audio.write(audio_data)
                temp_audio_path = temp_audio.name
            
            try:
                # Load and convert audio
                audio_segment = AudioSegment.from_file(temp_audio_path)
                
                # Convert to WAV format if needed
                if not temp_audio_path.endswith('.wav'):
                    audio_segment = audio_segment.set_frame_rate(16000).set_channels(1)
                    wav_path = temp_audio_path.replace(temp_audio_path.split('.')[-1], 'wav')
                    audio_segment.export(wav_path, format='wav')
                    temp_audio_path = wav_path
                
                # Perform speech recognition
                with sr.AudioFile(temp_audio_path) as source:
                    # Adjust for ambient noise
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    
                    # Record audio
                    audio = self.recognizer.record(source)
                    
                    # Recognize speech using Google Web Speech API
                    try:
                        text = self.recognizer.recognize_google(
                            audio, 
                            language=lang_config['code']
                        )
                        
                        return {
                            'success': True,
                            'text': text,
                            'language': language,
                            'confidence': 0.85,  # Google API doesn't provide confidence scores
                            'message': 'Speech successfully converted to text'
                        }
                        
                    except sr.UnknownValueError:
                        return {
                            'success': False,
                            'text': '',
                            'language': language,
                            'confidence': 0.0,
                            'message': 'Could not understand the audio'
                        }
                        
                    except sr.RequestError as e:
                        logger.error(f"Speech recognition service error: {e}")
                        return {
                            'success': False,
                            'text': '',
                            'language': language,
                            'confidence': 0.0,
                            'message': f'Speech recognition service unavailable: {e}'
                        }
                        
            finally:
                # Clean up temporary files
                if os.path.exists(temp_audio_path):
                    os.unlink(temp_audio_path)
                    
        except Exception as e:
            logger.error(f"Error in speech-to-text conversion: {e}")
            return {
                'success': False,
                'text': '',
                'language': language,
                'confidence': 0.0,
                'message': f'Error processing audio: {str(e)}'
            }

    def text_to_speech(self, text: str, language: str = 'en', slow: bool = False) -> Dict[str, Any]:
        """
        Convert text to speech audio
        
        Args:
            text: Text to convert to speech
            language: Language code ('en' or 'lg')
            slow: Whether to speak slowly
            
        Returns:
            Dict containing audio data and metadata
        """
        try:
            # Handle Luganda text - translate to English for TTS
            if language == 'lg':
                # For now, use English TTS for Luganda text
                # In production, you would integrate with a Luganda TTS service
                text = self._handle_luganda_text(text)
                tts_language = 'en'
            else:
                tts_language = language
            
            # Create gTTS object
            tts = gTTS(
                text=text,
                lang=tts_language,
                slow=slow
            )
            
            # Generate audio to memory
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            
            # Convert to WAV format for better compatibility
            audio_segment = AudioSegment.from_mp3(audio_buffer)
            wav_buffer = io.BytesIO()
            audio_segment.export(wav_buffer, format='wav')
            wav_buffer.seek(0)
            
            # Encode audio as base64 for JSON response
            audio_base64 = base64.b64encode(wav_buffer.getvalue()).decode('utf-8')
            
            return {
                'success': True,
                'audio_data': audio_base64,
                'audio_format': 'wav',
                'language': language,
                'text': text,
                'duration': len(audio_segment) / 1000.0,  # Duration in seconds
                'message': 'Text successfully converted to speech'
            }
            
        except Exception as e:
            logger.error(f"Error in text-to-speech conversion: {e}")
            return {
                'success': False,
                'audio_data': None,
                'audio_format': None,
                'language': language,
                'text': text,
                'duration': 0,
                'message': f'Error generating speech: {str(e)}'
            }

    def _handle_luganda_text(self, text: str) -> str:
        """
        Handle Luganda text for TTS
        This is a simplified version - in production you would use proper translation
        """
        # Basic Luganda to English mapping for common health terms
        luganda_mappings = {
            'muli mutya': 'how are you',
            'buli kirungi': 'everything is fine',
            'ndi bulungi': 'I am fine',
            'nnwadde': 'I am sick',
            'omutwe gunnuma': 'I have a headache',
            'nfuna omusujja': 'I have fever',
            'nkooye': 'I am coughing',
            'weebale': 'thank you',
            'webale nnyingi': 'thank you very much',
        }
        
        text_lower = text.lower()
        for luganda, english in luganda_mappings.items():
            if luganda in text_lower:
                text = text.replace(luganda, english)
        
        return text

    def process_audio_file(self, audio_file, language: str = 'en') -> Dict[str, Any]:
        """
        Process uploaded audio file for speech recognition
        
        Args:
            audio_file: Django uploaded file object
            language: Language code
            
        Returns:
            Dict containing processing results
        """
        try:
            # Read audio file content
            audio_data = audio_file.read()
            
            # Process speech-to-text
            result = self.speech_to_text(audio_data, language)
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing audio file: {e}")
            return {
                'success': False,
                'text': '',
                'language': language,
                'confidence': 0.0,
                'message': f'Error processing audio file: {str(e)}'
            }

    def get_supported_languages(self) -> Dict[str, Any]:
        """Get list of supported languages for voice processing"""
        return {
            'languages': self.supported_languages,
            'default': 'en',
            'message': 'Supported languages for voice processing'
        }

    def validate_audio_format(self, audio_file) -> Tuple[bool, str]:
        """
        Validate uploaded audio file format
        
        Args:
            audio_file: Django uploaded file object
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Supported formats
        supported_formats = ['.wav', '.mp3', '.m4a', '.ogg', '.flac', '.aac']
        
        # Check file extension
        file_extension = os.path.splitext(audio_file.name)[1].lower()
        
        if file_extension not in supported_formats:
            return False, f"Unsupported audio format. Supported formats: {', '.join(supported_formats)}"
        
        # Check file size (max 10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        if audio_file.size > max_size:
            return False, f"Audio file too large. Maximum size: 10MB"
        
        return True, "Audio file is valid"

class VoiceConsultationService:
    """Service for handling voice-based consultations"""
    
    def __init__(self):
        self.voice_processor = VoiceProcessingService()
    
    def process_voice_consultation(
        self, 
        audio_data: bytes, 
        consultation_id: str, 
        language: str = 'en'
    ) -> Dict[str, Any]:
        """
        Process voice input for a consultation
        
        Args:
            audio_data: Binary audio data
            consultation_id: ID of the consultation
            language: Language code
            
        Returns:
            Dict containing processed results
        """
        try:
            # Convert speech to text
            speech_result = self.voice_processor.speech_to_text(audio_data, language)
            
            if not speech_result['success']:
                return speech_result
            
            # Process the text through AI consultation service
            from .ai_consultation_service import AIConsultationService
            ai_service = AIConsultationService()
            
            ai_response = ai_service.process_consultation_message(
                consultation_id=consultation_id,
                message=speech_result['text'],
                language=language
            )
            
            # Generate voice response
            if ai_response.get('success') and ai_response.get('response'):
                voice_response = self.voice_processor.text_to_speech(
                    text=ai_response['response'],
                    language=language
                )
                
                return {
                    'success': True,
                    'transcribed_text': speech_result['text'],
                    'ai_response': ai_response['response'],
                    'voice_response': voice_response.get('audio_data'),
                    'audio_format': voice_response.get('audio_format'),
                    'language': language,
                    'consultation_id': consultation_id,
                    'message': 'Voice consultation processed successfully'
                }
            else:
                return {
                    'success': False,
                    'transcribed_text': speech_result['text'],
                    'ai_response': None,
                    'voice_response': None,
                    'language': language,
                    'consultation_id': consultation_id,
                    'message': 'Error processing AI response'
                }
                
        except Exception as e:
            logger.error(f"Error in voice consultation processing: {e}")
            return {
                'success': False,
                'transcribed_text': '',
                'ai_response': None,
                'voice_response': None,
                'language': language,
                'consultation_id': consultation_id,
                'message': f'Error processing voice consultation: {str(e)}'
            }

# Export services
voice_processing_service = VoiceProcessingService()
voice_consultation_service = VoiceConsultationService()
