# BulamuChainBot 🏥🤖

An AI-powered health assistant for rural Uganda with blockchain integration.

## 🎯 Project Overview

BulamuChainBot is a hackathon-ready health consultation chatbot designed for rural Uganda, featuring:

- **Multilingual Support**: English + Luganda consultations
- **Voice Integration**: Speech-to-text and text-to-speech capabilities
- **Blockchain Security**: Medical record hashes and medicine authentication
- **Mobile-First Design**: Clean, minimalist UI optimized for mobile devices

## 🏗️ Architecture

```
BulamuChainBot/
├── backend/           # Django + DRF API
├── frontend/          # Next.js + Tailwind CSS
├── smart_contracts/   # Solidity contracts
└── README.md
```

## 🚀 Features

### Core Functionality
- ✅ Text-based health consultations
- ✅ Voice input/output support
- ✅ Symptom analysis with AI
- ✅ Emergency detection
- ✅ Multilingual support (English + Luganda)

### Blockchain Integration
- ✅ Medical record hash storage
- ✅ Medicine authenticity verification via QR codes
- ✅ Testnet compatibility

### Security & Compliance
- ✅ JWT authentication
- ✅ Role-based access (Patient vs Doctor)
- ✅ End-to-end encryption mock
- ✅ GDPR/HIPAA compliant design

## 🛠️ Tech Stack

**Backend:**
- Django + Django REST Framework
- Web3.py for blockchain integration
- SQLite/PostgreSQL database
- Google Gemini/OpenAI for AI services

**Frontend:**
- Next.js + React
- Tailwind CSS
- Mobile-responsive design
- QR code scanner integration

**Blockchain:**
- Solidity smart contracts
- Web3.py integration
- Testnet deployment ready

## 🎨 UI Design

- **Theme**: Blue (#3399FF) + White (#FFFFFF)
- **Layout**: Minimalist, centered design
- **Logo**: Simple stethoscope SVG
- **Mobile-First**: Responsive across all devices

## 🚀 Quick Start

### Backend Setup
```bash
cd backend/
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Frontend Setup
```bash
cd frontend/
npm install
npm run dev
```

### Smart Contracts
```bash
cd smart_contracts/
# Smart contract deployment instructions
```

## 📱 API Endpoints

- `POST /api/consult` - Text health consultation
- `POST /api/consult-audio` - Voice consultation
- `POST /api/records/store` - Store medical record
- `GET /api/records/{id}` - Retrieve patient record
- `POST /api/medicine/verify` - QR code medicine verification

## 🏆 Hackathon Ready

This project is designed for rapid deployment and demonstration:
- Clean, organized code structure
- Mock services for heavy AI computations
- Sample seed data included
- Docker-ready configuration
- Environment variables for easy API key management

## 📄 License

MIT License - Perfect for hackathon use and further development.

---

**Built with ❤️ for rural Uganda healthcare accessibility**
