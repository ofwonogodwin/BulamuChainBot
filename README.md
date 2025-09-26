# BulamuChainBot 

A comprehensive blockchain-powered healthcare consultation platform that combines AI-driven medical assistance with secure medical record management on the blockchain.

## Overview

BulamuChainBot is an innovative healthcare technology solution designed to provide accessible medical consultations and secure medical record management for communities in Uganda and beyond. The platform leverages artificial intelligence, blockchain technology, and multi-language support to deliver quality healthcare services.

### Key Features

- **AI-Powered Medical Consultations** - Get instant medical advice using advanced AI models
- **Multi-Language Voice Support** - Consultations in English and Luganda
-  **Blockchain Medical Records** - Secure, immutable medical record storage
-  **Privacy & Consent Management** - Patient-controlled access to medical data
- **Emergency Detection** - AI-powered emergency situation identification
- **Modern Web Interface** - Responsive Next.js frontend with real-time updates
- **Voice Processing** - Speech-to-text and text-to-speech capabilities

## Architecture

### Backend (Django REST API)

- **Django 5.0.8** with REST Framework
- **JWT Authentication** with refresh token rotation
- **Multi-language AI Support** (OpenAI, Google Gemini, Sunbird AI)
- **Voice Processing** (Google Speech API, Azure Speech)
- **Blockchain Integration** (Web3.py for Ethereum)

### Frontend (Next.js)

- **Next.js 15** with TypeScript
- **Tailwind CSS** for responsive design
- **React Hooks** for state management
- **Axios** for API communication
- **Real-time notifications** with React Hot Toast

### Smart Contracts (Solidity)

- **Medical Records Contract** - Secure hash storage with consent management
- **Medicine Authentication** - Anti-counterfeit verification system
- **Ethereum Sepolia** testnet deployment

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL (optional, SQLite included)
- Ethereum wallet (for blockchain features)

### Backend Setup

1. **Clone and navigate to backend**

   ```bash
   git clone https://github.com/Marcelofury/BulamuChainBot.git
   cd BulamuChainBot/backend
   ```

2. **Create virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Environment configuration**

   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

5. **Database setup**

   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

6. **Start development server**

   ```bash
   python manage.py runserver
   ```

### Frontend Setup

1. **Navigate to frontend directory**

   ```bash
   cd ../frontend
   ```

2. **Install dependencies**

   ```bash
   npm install
   ```

3. **Start development server**

   ```bash
   npm run dev
   ```

### Smart Contracts Setup



Create a `.env` file in the backend directory:

```env
# Django Configuration
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (Optional - defaults to SQLite)
DATABASE_URL=postgresql://user:pass@localhost/bulamuchain

# AI Services
OPENAI_API_KEY=your-openai-key
GOOGLE_GEMINI_API_KEY=your-gemini-key
SUNBIRD_AI_API_KEY=your-sunbird-key

# Speech Services
GOOGLE_SPEECH_API_KEY=your-google-speech-key
AZURE_SPEECH_KEY=your-azure-speech-key
AZURE_SPEECH_REGION=your-azure-region

# Blockchain
WEB3_PROVIDER_URL=https://sepolia.infura.io/v3/your-infura-key
PRIVATE_KEY=your-ethereum-private-key
CONTRACT_ADDRESS_MEDICAL_RECORDS=deployed-contract-address
CONTRACT_ADDRESS_MEDICINE_AUTH=deployed-medicine-contract-address

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### Authentication Endpoints

- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User authentication
- `POST /api/auth/refresh/` - Token refresh
- `POST /api/auth/logout/` - User logout

### Consultation Endpoints

- `GET /api/consultations/` - List user consultations
- `POST /api/consultations/` - Start new consultation
- `GET /api/consultations/{id}/` - Get consultation details
- `POST /api/consultations/{id}/messages/` - Send message
- `POST /api/consultations/voice/` - Voice consultation

### Medical Records Endpoints

- `GET /api/records/` - List medical records
- `POST /api/records/` - Store medical record
- `GET /api/records/{id}/` - Get record details
- `POST /api/records/{id}/consent/` - Manage consent

### Blockchain Endpoints

- `POST /api/blockchain/store-record/` - Store record hash on blockchain
- `GET /api/blockchain/verify-record/` - Verify record integrity
- `POST /api/blockchain/grant-consent/` - Grant provider access
- `POST /api/blockchain/revoke-consent/` - Revoke provider access


## Multi-Language Support

The platform supports:

- **English** - Primary language for international users
- **Luganda** - Local language support for Ugandan users
- Swahili

Voice recognition and synthesis available in both languages using:

- Google Speech-to-Text API
- Azure Cognitive Services
- Google Text-to-Speech

## Security Features

- **JWT Authentication** with automatic token refresh
- **Blockchain Immutability** for medical records
- **Patient Consent Management** with smart contracts
- **Encrypted Data Storage** using industry standards
- **CORS Protection** for API security
- **Input Validation** and sanitization

## Emergency Detection

The AI system monitors consultations for emergency indicators:

- **Severity Scoring** (1-10 scale)
- **Automatic Alerts** for critical conditions
- **Emergency Contact** notifications
- **Healthcare Provider** escalation

## Getting the Project
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 for Python code
- Use TypeScript for frontend development
- Write tests for new features
- Update documentation for API changes
- Follow semantic versioning


### Phase 1 (Current)

- Core consultation system
- Blockchain medical records
- Multi-language support
- Emergency detection

### Phase 3 (Future)

- 🤖vanced AI diagnostics
- Multi-country deployment
- Mobile applications
- IoT device integration


