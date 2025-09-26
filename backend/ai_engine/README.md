# AI Engine - Intelligent Medical Chatbot

## Overview
The AI Engine is a comprehensive Retrieval-Augmented Generation (RAG) system designed specifically for medical consultations in Uganda. It combines advanced language models, vector databases, and medical knowledge bases to provide intelligent, context-aware healthcare assistance.

## Features

### 🤖 Intelligent Conversational AI
- **Advanced RAG System**: Combines retrieval with generation for accurate medical responses
- **Conversation Memory**: Maintains context across multiple interactions
- **Multilingual Support**: English, Luganda, and Swahili
- **Emergency Detection**: Automatically identifies and responds to emergency situations
- **Cultural Sensitivity**: Adapted for Ugandan healthcare context

### 🧠 Medical Knowledge Base
- **Comprehensive Coverage**: Infectious diseases, maternal health, NCDs, mental health
- **Local Context**: Uganda-specific health information and prevalence data
- **Symptoms Analysis**: Intelligent symptom-to-condition mapping
- **Treatment Guidelines**: Evidence-based treatment recommendations
- **Prevention Strategies**: Culturally appropriate preventive care guidance

### 🔍 Vector Search & RAG
- **Multiple Vector Stores**: Chroma and FAISS integration
- **Semantic Search**: Advanced similarity matching for medical queries
- **Ensemble Retrieval**: Combines vector search with BM25 for optimal results
- **Dynamic Knowledge Updates**: Real-time addition of new medical information

### 🎤 Voice Integration
- **Speech-to-Text**: Voice query processing
- **Text-to-Speech**: Audio responses in multiple languages
- **Voice Chat Sessions**: Complete voice interaction capability

### 🚨 Emergency Response
- **Real-time Detection**: Identifies emergency keywords and situations
- **Immediate Guidance**: Provides critical emergency instructions
- **Healthcare Provider Integration**: Direct referral recommendations

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    AI Engine Architecture                   │
├─────────────────────────────────────────────────────────────┤
│  Frontend Interface                                         │
│  ├── Web Chat UI                                           │
│  ├── Voice Chat Interface                                  │
│  └── Mobile App Integration                                │
├─────────────────────────────────────────────────────────────┤
│  API Layer (Django Views)                                  │
│  ├── Intelligent Chat Endpoints                           │
│  ├── RAG Search API                                        │
│  ├── Voice Processing API                                  │
│  └── Knowledge Management API                              │
├─────────────────────────────────────────────────────────────┤
│  Core AI Engine Components                                 │
│  ├── IntelligentMedicalChatbot                            │
│  │   ├── Conversation Management                          │
│  │   ├── Emergency Detection                              │
│  │   ├── Language Processing                              │
│  │   └── Response Generation                              │
│  │                                                        │
│  ├── RAGEngine                                            │
│  │   ├── Context Retrieval                               │
│  │   ├── Response Generation                              │
│  │   ├── Source Attribution                              │
│  │   └── Performance Metrics                             │
│  │                                                        │
│  ├── VectorStoreManager                                   │
│  │   ├── Chroma Vector Store                             │
│  │   ├── FAISS Vector Store                              │
│  │   ├── BM25 Retrieval                                  │
│  │   └── Ensemble Search                                 │
│  │                                                        │
│  └── MedicalKnowledgeBase                                 │
│      ├── Medical Conditions Database                      │
│      ├── Symptoms Mapping                                 │
│      ├── Emergency Protocols                              │
│      ├── Treatment Guidelines                             │
│      └── Cultural Context                                 │
├─────────────────────────────────────────────────────────────┤
│  External Services                                          │
│  ├── Google Gemini 2.5 Flash (LLM)                       │
│  ├── Google Embeddings API                                │
│  ├── Speech-to-Text Service                               │
│  └── Text-to-Speech Service                               │
├─────────────────────────────────────────────────────────────┤
│  Data Storage                                              │
│  ├── Vector Databases (Chroma/FAISS)                      │
│  ├── Conversation Cache (Redis)                           │
│  ├── Knowledge Base Files                                 │
│  └── User Session Data                                    │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### IntelligentMedicalChatbot
The main orchestrator that manages conversations and coordinates all AI services.

**Key Features:**
- Session management with automatic timeout
- Multi-turn conversation support
- Emergency situation handling
- Personality and empathy integration
- Performance monitoring

### RAGEngine
Advanced retrieval-augmented generation system for medical knowledge.

**Capabilities:**
- Multi-strategy document retrieval
- Context-aware response generation
- Source attribution and verification
- Real-time knowledge base updates
- Performance optimization

### VectorStoreManager
Manages vector embeddings and similarity search across multiple stores.

**Features:**
- Dual vector store support (Chroma + FAISS)
- Embedding generation with Google AI
- Ensemble retrieval combining vector and keyword search
- Automatic persistence and loading

### MedicalKnowledgeBase
Comprehensive medical information database with Ugandan context.

**Coverage Areas:**
- **Infectious Diseases**: Malaria, Typhoid, TB, HIV/AIDS
- **Maternal & Child Health**: Pregnancy care, immunizations
- **Non-Communicable Diseases**: Diabetes, Hypertension, Cancer
- **Mental Health**: Depression, anxiety, cultural considerations
- **Emergency Medicine**: Protocols and immediate care guidelines

## API Endpoints

### Chat Endpoints
```
POST /api/ai/intelligent-chat/          # Main chat interface
POST /api/ai/start-conversation/        # Initialize session
POST /api/ai/end-conversation/         # End session
POST /api/ai/voice-chat/               # Voice interaction
```

### Search Endpoints
```
GET  /api/ai/rag-search/               # RAG-enhanced search
GET  /api/ai/knowledge-search/         # Direct knowledge base search
POST /api/ai/symptom-analysis/         # Symptom analysis
```

### System Endpoints
```
GET  /api/ai/status/                   # System health and metrics
POST /api/ai/add-knowledge/            # Add new medical knowledge
POST /api/ai/legacy-chat/              # Backward compatibility
```

## Usage Examples

### Basic Chat
```python
import requests

# Start conversation
response = requests.post('http://localhost:8001/api/ai/start-conversation/', {
    'user_id': 'user123',
    'language': 'english',
    'session_data': {'user_name': 'John'}
})

conversation_id = response.json()['conversation_id']

# Send message
response = requests.post('http://localhost:8001/api/ai/intelligent-chat/', {
    'conversation_id': conversation_id,
    'message': 'I have a fever and headache',
    'language': 'english'
})

print(response.json()['response']['answer'])
```

### Symptom Analysis
```python
response = requests.post('http://localhost:8001/api/ai/symptom-analysis/', {
    'symptoms': ['fever', 'headache', 'muscle aches'],
    'language': 'english'
})

analysis = response.json()['analysis']
print(f"Possible conditions: {analysis['possible_conditions']}")
print(f"Recommendation: {analysis['recommendation']}")
```

### RAG Search
```python
response = requests.get('http://localhost:8001/api/ai/rag-search/', {
    'query': 'How to prevent malaria?',
    'language': 'luganda'
})

result = response.json()['result']
print(f"Answer: {result['answer']}")
print(f"Sources: {result.get('sources', [])}")
```

## Configuration

### Environment Variables
```bash
# Required
GOOGLE_GEMINI_API_KEY=your_gemini_api_key

# Optional
AI_ENGINE_DEBUG=True
VECTOR_STORE_PERSIST_DIR=/path/to/vector/store
CONVERSATION_TIMEOUT=3600  # 1 hour
MAX_CONVERSATION_MEMORY=10  # Number of exchanges to remember
```

### Django Settings
```python
# Add to INSTALLED_APPS
INSTALLED_APPS = [
    # ... existing apps
    'ai_engine',
]

# AI Engine specific settings
AI_ENGINE_CONFIG = {
    'DEFAULT_LANGUAGE': 'english',
    'SUPPORTED_LANGUAGES': ['english', 'luganda', 'swahili'],
    'ENABLE_VOICE_CHAT': True,
    'ENABLE_EMERGENCY_DETECTION': True,
    'RAG_CONTEXT_MAX_TOKENS': 2000,
    'CONVERSATION_MEMORY_SIZE': 10,
}
```

## Installation & Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your API keys
```

### 3. Initialize Vector Stores
```bash
python manage.py shell
>>> from ai_engine import IntelligentMedicalChatbot
>>> chatbot = IntelligentMedicalChatbot()
>>> print("AI Engine initialized successfully!")
```

### 4. Run Migrations
```bash
python manage.py migrate
```

### 5. Start Server
```bash
python manage.py runserver 8001
```

## Performance Metrics

The AI Engine tracks comprehensive metrics:

- **Response Times**: Average and percentile response times
- **Retrieval Success**: Rate of successful context retrieval
- **Conversation Statistics**: Active sessions, message counts
- **Emergency Detection**: Number of emergencies handled
- **Knowledge Base Usage**: Most queried topics and conditions

Access metrics via: `GET /api/ai/status/`

## Multilingual Support

### Supported Languages
1. **English**: Primary language with full feature support
2. **Luganda**: Native Ugandan language with cultural context
3. **Swahili**: Regional language for broader accessibility

### Language Features
- Automatic language detection
- Medical term translations
- Cultural health practices integration
- Region-specific health information

## Emergency Response System

### Detection Capabilities
- Real-time keyword monitoring
- Severity assessment
- Automatic escalation protocols
- Multi-language emergency phrases

### Response Features
- Immediate emergency instructions
- Healthcare facility recommendations
- Emergency contact information
- Follow-up guidance while waiting for help

## Security & Privacy

### Data Protection
- No storage of personal health information
- Session-based conversation memory only
- Automatic session cleanup
- Encrypted API communications

### Medical Disclaimers
- Clear limitations of AI advice
- Emphasis on professional medical consultation
- Emergency situation prioritization
- Source attribution for medical information

## Extensibility

### Adding New Medical Knowledge
```python
# Example: Adding new condition information
new_knowledge = {
    'conditions': [{
        'condition': 'COVID-19',
        'symptoms': ['fever', 'cough', 'loss of taste'],
        'treatment': 'Rest, hydration, medical monitoring',
        'prevention': 'Vaccination, masks, social distancing'
    }]
}

# Add via API
response = requests.post('/api/ai/add-knowledge/', {
    'knowledge_data': new_knowledge
})
```

### Custom Language Support
1. Add translations to `MedicalKnowledgeBase._load_translations()`
2. Update language mappings in medical conditions
3. Extend prompt templates for new language
4. Test emergency detection keywords

### Integration Points
- **Frontend**: React/Vue.js integration via REST APIs
- **Mobile**: React Native or native mobile app integration
- **Voice**: Custom speech service integration
- **Analytics**: Custom metrics and logging integration

## Development

### Running Tests
```bash
pytest ai_engine/tests/
```

### Code Quality
```bash
black ai_engine/
flake8 ai_engine/
```

### Development Server
```bash
python manage.py runserver 8001 --settings=bulamuchain.settings.development
```

## Production Deployment

### Environment Setup
1. Configure production environment variables
2. Set up persistent vector store storage
3. Configure Redis for conversation caching
4. Enable proper logging and monitoring

### Performance Optimization
- Use dedicated GPU instances for embeddings
- Implement connection pooling for vector databases
- Set up CDN for static medical resources
- Configure load balancing for high availability

### Monitoring
- Health checks for all AI services
- Performance metrics dashboard
- Error tracking and alerting
- Usage analytics and reporting

## License

This AI Engine is part of the BulamuChainBot project and follows the same licensing terms.

---

**Disclaimer**: This AI system is designed to provide health information and support, but it is not a replacement for professional medical advice, diagnosis, or treatment. Always seek the advice of qualified healthcare providers with any questions regarding medical conditions.
