"""
AI and Emergency Detection Services for BulamuChainBot
"""
import openai
import json
import re
from django.conf import settings
from django.contrib.auth import get_user_model
from .models import Consultation, EmergencyAlert
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

class AIConsultationService:
    """
    Service for processing health consultations with AI
    """
    
    def __init__(self):
        self.openai_key = getattr(settings, 'OPENAI_API_KEY', '')
        if self.openai_key:
            openai.api_key = self.openai_key
    
    def analyze_symptoms(self, symptoms_text, language='en', user=None):
        """
        Analyze patient symptoms using AI
        """
        try:
            # Create context-aware prompt
            prompt = self._create_symptom_analysis_prompt(symptoms_text, language, user)
            
            if self.openai_key:
                response = self._call_openai_api(prompt)
            else:
                # Fallback mock response for development
                response = self._mock_ai_response(symptoms_text, language)
            
            return self._parse_ai_response(response)
            
        except Exception as e:
            logger.error(f"AI analysis error: {str(e)}")
            return self._fallback_response(symptoms_text, language)
    
    def process_audio_consultation(self, audio_file, language='en', user=None):
        """
        Process audio consultation with speech-to-text and AI analysis
        """
        try:
            # Mock transcription for now (would integrate with Google Speech API)
            transcription = self._mock_transcribe_audio(audio_file, language)
            
            # Analyze transcribed text
            analysis = self.analyze_symptoms(transcription, language, user)
            analysis['transcription'] = transcription
            
            return analysis
            
        except Exception as e:
            logger.error(f"Audio consultation error: {str(e)}")
            return {
                'transcription': '[Audio transcription failed]',
                'response': 'I apologize, but I had trouble processing your audio. Please try again or use text instead.',
                'severity_score': 5,
                'recommendations': 'Please consult with a healthcare provider for proper diagnosis.'
            }
    
    def generate_followup_response(self, consultation, new_message):
        """
        Generate AI response for follow-up messages in consultation
        """
        try:
            conversation_context = self._build_conversation_context(consultation, new_message)
            
            if self.openai_key:
                response = self._call_openai_api(conversation_context)
            else:
                response = self._mock_followup_response(new_message)
            
            return {'response': response}
            
        except Exception as e:
            logger.error(f"Followup response error: {str(e)}")
            return {
                'response': 'Thank you for the additional information. Could you tell me more about your symptoms?'
            }
    
    def _create_symptom_analysis_prompt(self, symptoms, language, user):
        """
        Create contextual prompt for symptom analysis
        """
        if language == 'lg':  # Luganda
            base_prompt = """
            Oli musawo wa AI eyamba abantu mu Uganda. Omuntu akubuulizza ebikwata ku bulwadde bwe:
            
            Obubaka bw'omulwadde: "{symptoms}"
            
            Muwe okuddamu okukola:
            1. Okwetegereza ebimukwatako
            2. Ebiragiro bya maanyi (1-10, 10 nga kya maanyi ennyo)
            3. Ebyokukola
            4. Singa kyetaaga okujjayo ku ddwaliro amangu
            
            Ddamu mu Luganda era oba mukwano.
            """
        else:  # English
            base_prompt = """
            You are a helpful AI health assistant for rural Uganda. A patient has described their symptoms:
            
            Patient symptoms: "{symptoms}"
            
            Provide a response that includes:
            1. Symptom analysis and possible causes
            2. Severity assessment (1-10 scale, 10 being most severe)
            3. Recommended actions and self-care
            4. When to seek immediate medical attention
            
            Be empathetic, culturally sensitive, and always recommend professional medical consultation for serious concerns.
            Keep responses clear and accessible for rural communities.
            
            IMPORTANT: You are not providing medical diagnosis, only general health guidance.
            """
        
        return base_prompt.format(symptoms=symptoms)
    
    def _call_openai_api(self, prompt):
        """
        Call OpenAI API for symptom analysis
        """
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful medical AI assistant focused on Ugandan healthcare."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise
    
    def _mock_ai_response(self, symptoms, language):
        """
        Mock AI response for development/testing
        """
        if language == 'lg':
            return """
            Nsiima nti onnyonnyodde ebikukwatako. Okusinziira ku bye onjuddeko:

            Okwetegereza: Obubaka bwo bukakasa nti olina obulwadde obw'okubuubuuka oba omusujja. Ebintu ebyo bisobola okuva mu kukozesa emmere embi oba amazzi agali mu bucaafu.

            Obukulu: 4/10 (si bunene naye beetaaga okubifaako)

            Ebyokukola:
            • Nywa amazzi mangi agalongose
            • Wewale emmere enkalu n'ebitali birungi
            • Webaka bulungi
            • Kola ku mubiri gwo oleme okukopeka endala

            Jja ku ddwaliro singa: Ebimukwatako singa byeyongera, singa ofuna omusujja ogw'amaanyi, oba singa tossobola kunnywa mazzi.
            """
        else:
            return """
            Thank you for describing your symptoms. Based on what you've shared:

            Analysis: Your symptoms suggest you may have a common cold or flu-like illness. This could be due to viral infection, which is common during season changes.

            Severity Level: 4/10 (mild to moderate, manageable with self-care)

            Recommended Actions:
            • Rest and get plenty of sleep
            • Drink warm fluids like tea or warm water
            • Eat light, nutritious foods
            • Use honey for throat irritation
            • Maintain good hygiene to prevent spreading

            Seek immediate care if: Symptoms worsen, you develop high fever (above 38.5°C), difficulty breathing, or cannot keep fluids down.

            Remember: This is general guidance only. Please consult a healthcare provider for proper diagnosis and treatment.
            """
    
    def _mock_followup_response(self, message):
        """
        Mock followup response
        """
        return "Thank you for providing more information. Based on what you've shared, I recommend continuing to monitor your symptoms and maintaining the self-care measures I mentioned earlier. If your condition doesn't improve in the next 24-48 hours, please consider visiting a healthcare facility."
    
    def _mock_transcribe_audio(self, audio_file, language):
        """
        Mock audio transcription (would use Google Speech API in production)
        """
        if language == 'lg':
            return "Nze nnina obusujja n'omulimu. Nfuna okuwunyisa n'okukula mu mubiri gwange."
        else:
            return "I have been having a headache and fever for the past two days. I also feel tired and have body aches."
    
    def _parse_ai_response(self, ai_response):
        """
        Parse AI response to extract severity score and recommendations
        """
        severity_score = 5  # Default
        
        # Try to extract severity score from response
        severity_match = re.search(r'(\d+)/10|severity[:\s]*(\d+)', ai_response.lower())
        if severity_match:
            score = int(severity_match.group(1) or severity_match.group(2))
            if 1 <= score <= 10:
                severity_score = score
        
        # Split response into main response and recommendations
        recommendations = ""
        if "recommended actions:" in ai_response.lower() or "ebyokukola:" in ai_response.lower():
            parts = re.split(r'(?i)recommended actions?:|ebyokukola:', ai_response, 1)
            if len(parts) == 2:
                recommendations = parts[1].strip()
        
        return {
            'response': ai_response,
            'severity_score': severity_score,
            'recommendations': recommendations or ai_response
        }
    
    def _build_conversation_context(self, consultation, new_message):
        """
        Build conversation context for follow-up responses
        """
        context = f"""
        Previous conversation context:
        Original symptoms: {consultation.symptoms_text}
        Previous AI response: {consultation.ai_response}
        
        New patient message: {new_message}
        
        Provide a helpful follow-up response that acknowledges the new information and provides additional guidance.
        """
        return context
    
    def _fallback_response(self, symptoms, language):
        """
        Fallback response when AI services fail
        """
        if language == 'lg':
            response = """
            Nsiima nti onnyonnyodde ebikukwatako. Olw'okulemwa mu puloguramu, sisobola kukuwa okuddamu okw'omugaso nga bwe njagala.
            
            Nkusaba ojje ku ddwaliro okufuna obujjanjabi obw'amazima okuva ku basawo ab'omugaso.
            """
        else:
            response = """
            Thank you for sharing your symptoms with me. Due to a technical issue, I cannot provide the detailed analysis you deserve right now.
            
            I strongly recommend visiting a healthcare facility or consulting with a medical professional for proper evaluation and treatment.
            """
        
        return {
            'response': response,
            'severity_score': 5,
            'recommendations': 'Please consult with a healthcare provider for proper medical evaluation.'
        }

    def chat_with_ai(self, message, language='en', conversation_history=None):
        """
        Chat with AI using Gemini for health consultation
        """
        try:
            # Import Google Generative AI
            import google.generativeai as genai
            
            # Configure Gemini API
            gemini_api_key = getattr(settings, 'GOOGLE_GEMINI_API_KEY', '')
            if not gemini_api_key:
                return self._fallback_chat_response(message, language)
            
            genai.configure(api_key=gemini_api_key)
            
            # Create the model
            model = genai.GenerativeModel('models/gemini-2.5-flash')
            
            # Build context with conversation history
            context = self._build_chat_context(message, language, conversation_history)
            
            # Generate response
            response = model.generate_content(context)
            
            return {
                'response': response.text if response.text else self._fallback_chat_response(message, language)['response'],
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            return self._fallback_chat_response(message, language)

    def _build_chat_context(self, message, language, conversation_history=None):
        """
        Build chat context for Gemini API
        """
        language_instructions = {
            'en': "Respond in English",
            'lg': "Respond in Luganda (a Ugandan language)",
            'sw': "Respond in Swahili"
        }
        
        base_prompt = f"""You are BulamuChainBot, an AI health assistant designed specifically for rural and underserved communities in Uganda. 

Your role:
- Provide helpful, accurate health information and guidance
- Be empathetic and culturally sensitive
- Always recommend consulting healthcare professionals for serious concerns
- Keep responses concise but informative
- {language_instructions.get(language, 'Respond in English')}

Guidelines:
- Don't diagnose medical conditions
- Provide general health guidance and first aid information
- Encourage seeking professional medical help when needed
- Be supportive and understanding
- Consider the rural Ugandan context in your responses

"""

        if conversation_history and len(conversation_history) > 0:
            base_prompt += "\nConversation history:\n"
            for msg in conversation_history[-5:]:  # Last 5 messages for context
                role = "User" if msg.get('isUser') else "Assistant"
                base_prompt += f"{role}: {msg.get('content', '')}\n"
        
        base_prompt += f"\nUser's current message: {message}\n\nPlease provide a helpful response:"
        
        return base_prompt

    def _fallback_chat_response(self, message, language):
        """
        Enhanced fallback response system when Gemini API is not available
        """
        message_lower = message.lower()
        
        # Common health conditions and responses
        health_responses = {
            'en': {
                'headache': "For headaches, try resting in a quiet, dark room. Stay hydrated and consider applying a cold compress to your forehead. If headaches persist or are severe, please consult a healthcare provider.",
                'fever': "For fever, rest and drink plenty of fluids. You can use paracetamol or ibuprofen to reduce fever. Monitor your temperature and seek medical care if fever is above 38.5°C (101°F) or persists.",
                'cough': "For persistent cough, stay hydrated, use honey for throat soothing, and avoid irritants. If cough lasts more than 3 weeks, has blood, or comes with difficulty breathing, see a doctor immediately.",
                'stomach': "For stomach issues, try eating bland foods, staying hydrated with small sips of water, and avoiding dairy or fatty foods. If you have severe pain, vomiting, or blood in stool, seek immediate medical attention.",
                'pain': "For pain management, rest the affected area and consider over-the-counter pain relievers if appropriate. Apply ice for injuries or heat for muscle tension. Persistent or severe pain needs medical evaluation.",
                'tired': "Fatigue can be due to lack of sleep, stress, or underlying conditions. Ensure 7-9 hours of sleep, eat nutritious meals, and stay hydrated. If fatigue persists despite rest, consult a healthcare provider.",
                'malaria': "Malaria prevention: Use mosquito nets, wear long sleeves at dusk/dawn, and use repellent. Symptoms include fever, chills, and headache. Seek immediate medical care if you suspect malaria.",
                'default': "I understand your health concern. While I can provide general guidance, it's important to consult with a healthcare professional for proper diagnosis and treatment. Please describe your symptoms in more detail."
            },
            'lg': {
                'headache': "Omutwe singa gukubagira, wewummule mu kisenge ekisiikiris era ekiziba. Nywa amazzi mangi era teeka ekintu ekinnyogovu ku kyenyi kyo. Singa omutwe gukubya buli kaseera, laba omusawo.",
                'fever': "Omusujja singa guli, wewummule era nywa amazzi mangi. Osobola okukozesa panadol okukakkanya omusujja. Singa omusujja gusukka 38.5°C oba gukyeyongera, laba omusawo amangu.",
                'cough': "Okukoola kw'emirembe egiwanvu, nywa amazzi mangi era kozesa omubisi gw'enjuki okuwonyawo omumiro. Singa okukoola kukyeyongera oba kuliko omusai, laba omusawo amangu.",
                'stomach': "Olubuto singa lukubagira, lya emmere entono era nywa amazzi matono matono. Weekweke amata n'emmere ezimu masavu. Singa olina obulumi obungi, laba omusawo.",
                'pain': "Obulumi, wewummule ekitundu ekikubagira era kozesa eddagala ly'obulumi eritembebwa mu dduka singa kikulu. Singa obulumi bukeyongera, laba omusawo.",
                'tired': "Okukoowa kuyinza okuva mu butamattidde, okwesigisa oba obulwadde obulala. Webaka essaawa 7-9, lya emmere engimu, era nywa amazzi mangi.",
                'malaria': "Okuziyiza omusujja gw'ensiri: kozesa akatimba k'ensiri, bambala engoye empanvu nga obudde buwungeera, era kozesa eddagala ly'ensiri.",
                'default': "Ntegeera ekirakubidde ku bulamu bwo. Newankubadde nsobola okukuwa amagezi ag'okutandikira, kikulu olabe omusawo omukugu okufuna obujjanjabi obututuufu."
            }
        }
        
        # Find relevant response based on keywords
        responses = health_responses.get(language, health_responses['en'])
        
        for condition, response in responses.items():
            if condition != 'default' and condition in message_lower:
                return {
                    'response': response,
                    'success': False
                }
        
        # Default response
        return {
            'response': responses['default'],
            'success': False
        }

class EmergencyDetectionService:
    """
    Service for detecting medical emergencies from symptoms
    """
    
    # Emergency keywords in English and Luganda
    EMERGENCY_KEYWORDS = {
        'en': [
            'chest pain', 'difficulty breathing', 'can\'t breathe', 'shortness of breath',
            'severe headache', 'unconscious', 'bleeding heavily', 'severe bleeding',
            'heart attack', 'stroke', 'seizure', 'convulsions', 'high fever',
            'severe abdominal pain', 'vomiting blood', 'difficulty swallowing',
            'severe allergic reaction', 'anaphylaxis', 'poisoning', 'overdose'
        ],
        'lg': [
            'okumpi mu kifuba', 'okusindika', 'sisobola kussaamu mukka', 'omutwe gukuba ennyo',
            'okuzibwa', 'omusai gुल्छ ennyo', 'okukwata omutima', 'endwadde y\'omutima',
            'okukankana', 'omusujja omungi ennyo', 'okutsuka omusai', 'okulumwa mu lubuto'
        ]
    }
    
    def detect_emergency(self, consultation):
        """
        Detect if consultation indicates emergency
        """
        return self.detect_emergency_from_text(
            consultation.symptoms_text, 
            {'severity_score': consultation.severity_score}
        )
    
    def detect_emergency_from_text(self, symptoms_text, ai_response=None):
        """
        Detect emergency from symptoms text
        """
        symptoms_lower = symptoms_text.lower()
        
        # Check for emergency keywords
        all_keywords = self.EMERGENCY_KEYWORDS['en'] + self.EMERGENCY_KEYWORDS['lg']
        for keyword in all_keywords:
            if keyword in symptoms_lower:
                return True
        
        # Check AI severity score
        if ai_response and ai_response.get('severity_score', 0) >= 8:
            return True
        
        return False
    
    def create_emergency_alert(self, consultation, ai_response=None):
        """
        Create emergency alert for healthcare providers
        """
        severity_score = consultation.severity_score or (ai_response.get('severity_score', 5) if ai_response else 5)
        
        # Determine alert level based on severity
        if severity_score >= 9:
            alert_level = 'critical'
        elif severity_score >= 7:
            alert_level = 'high'
        else:
            alert_level = 'medium'
        
        alert = EmergencyAlert.objects.create(
            consultation=consultation,
            alert_level=alert_level,
            symptoms_detected=consultation.symptoms_text,
            ai_recommendation=consultation.ai_response or (ai_response.get('response', '') if ai_response else '')
        )
        
        # TODO: Send notifications to healthcare providers
        self._notify_healthcare_providers(alert)
        
        return alert
    
    def _notify_healthcare_providers(self, alert):
        """
        Send notifications to available healthcare providers
        """
        # TODO: Implement notification system (email, SMS, push notifications)
        logger.info(f"Emergency alert created: {alert.id} - {alert.alert_level}")
        pass
