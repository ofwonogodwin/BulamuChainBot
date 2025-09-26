"""
URL patterns for AI Engine endpoints
"""

from django.urls import path
from . import views

app_name = 'ai_engine'

urlpatterns = [
    # Main intelligent chat endpoints
    path('intelligent-chat/', views.intelligent_chat, name='intelligent_chat'),
    path('start-conversation/', views.start_intelligent_conversation, name='start_conversation'),
    path('end-conversation/', views.end_intelligent_conversation, name='end_conversation'),
    
    # Voice chat
    path('voice-chat/', views.intelligent_voice_chat, name='voice_chat'),
    
    # RAG and knowledge search
    path('rag-search/', views.rag_search, name='rag_search'),
    path('knowledge-search/', views.medical_knowledge_search, name='knowledge_search'),
    path('symptom-analysis/', views.symptom_analysis, name='symptom_analysis'),
    
    # System management
    path('status/', views.chatbot_status, name='chatbot_status'),
    path('add-knowledge/', views.add_medical_knowledge, name='add_knowledge'),
    
    # Legacy compatibility
    path('legacy-chat/', views.legacy_chat, name='legacy_chat'),
]
