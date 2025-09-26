"""
AI Engine Package
Comprehensive RAG-powered medical AI system with LangChain and vector databases
"""

try:
    # Core components
    from .rag_engine import RAGEngine
    from .vector_store import VectorStoreManager
    from .knowledge_base import MedicalKnowledgeBase
    from .intelligent_chatbot import IntelligentMedicalChatbot

    __version__ = "1.0.0"

    __all__ = [
        'RAGEngine',
        'VectorStoreManager', 
        'MedicalKnowledgeBase',
        'IntelligentMedicalChatbot'
    ]
    
    # Test imports
    print("✅ AI Engine components loaded successfully")
    
except ImportError as e:
    print(f"⚠️ AI Engine import warning: {e}")
    # Provide fallback imports or graceful degradation
    pass

from .rag_engine import RAGEngine
from .vector_store import VectorStoreManager
from .knowledge_base import MedicalKnowledgeBase
from .intelligent_chatbot import IntelligentMedicalChatbot

__all__ = [
    'RAGEngine',
    'VectorStoreManager', 
    'MedicalKnowledgeBase',
    'IntelligentMedicalChatbot'
]
