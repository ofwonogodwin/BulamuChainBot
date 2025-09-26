from django.urls import path
from . import views
from . import voice_views
from .langchain_views import (
    langchain_ai_chat, 
    langchain_voice_chat, 
    LangChainChatSessionView,
    test_langchain_service
)

urlpatterns = [
    # Main consultation endpoints
    path('', views.ConsultationListCreateView.as_view(), name='consultation-list-create'),
    path('<uuid:pk>/', views.ConsultationDetailView.as_view(), name='consultation-detail'),
    
    # Specialized consultation endpoints
    path('consult/', views.TextConsultationView.as_view(), name='text-consultation'),
    path('consult-audio/', views.AudioConsultationView.as_view(), name='audio-consultation'),
    
    # Consultation messages
    path('<uuid:consultation_id>/messages/', views.ConsultationMessagesView.as_view(), name='consultation-messages'),
    
    # Emergency alerts
    path('emergency-alerts/', views.EmergencyAlertListView.as_view(), name='emergency-alerts'),
    path('emergency-alerts/<uuid:alert_id>/acknowledge/', views.acknowledge_emergency_alert, name='acknowledge-alert'),
    
    # AI Chat endpoint
    path('ai-chat/', views.ai_chat, name='ai-chat'),
    
    # Voice endpoints
    path('speech-to-text/', voice_views.speech_to_text, name='speech-to-text'),
    path('text-to-speech/', voice_views.text_to_speech, name='text-to-speech'),
    path('<uuid:consultation_id>/voice/', voice_views.VoiceConsultationView.as_view(), name='voice-consultation'),
    path('messages/<int:message_id>/to-speech/', voice_views.VoiceMessageView.as_view(), name='message-to-speech'),
    path('voice/languages/', voice_views.supported_languages, name='voice-languages'),
    
    # LangChain Gemini 2.5 Flash endpoints
    path('langchain-chat/', langchain_ai_chat, name='langchain_ai_chat'),
    path('langchain-voice-chat/', langchain_voice_chat, name='langchain_voice_chat'),
    path('langchain-session/', LangChainChatSessionView.as_view(), name='langchain_session'),
    path('test-langchain/', test_langchain_service, name='test_langchain'),
]
