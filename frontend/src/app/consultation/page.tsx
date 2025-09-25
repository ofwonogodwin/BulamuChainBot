'use client';

import React, { useState, useEffect, useRef } from 'react';
import { consultationService } from '@/services/api';
import ProtectedRoute from '@/components/ProtectedRoute';
import { useAuth } from '@/contexts/AuthContext';

interface Message {
  id: string;
  message: string;
  is_ai_response: boolean;
  created_at: string;
  sender?: string;
}

interface Consultation {
  id: string;
  symptoms: string;
  status: string;
  urgency_level: string;
  language: string;
  created_at: string;
  updated_at: string;
}

function ConsultationPageContent() {
  const [consultation, setConsultation] = useState<Consultation | null>(null);
  const { user, logout } = useAuth();
  const [messages, setMessages] = useState<Message[]>([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [symptoms, setSymptoms] = useState('');
  const [language, setLanguage] = useState('English');
  const [urgencyLevel, setUrgencyLevel] = useState('low');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Check for initial symptoms from homepage
    const initialSymptoms = sessionStorage.getItem('initialSymptoms');
    if (initialSymptoms) {
      setSymptoms(initialSymptoms);
      sessionStorage.removeItem('initialSymptoms');
    }
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const startConsultation = async () => {
    if (!symptoms.trim()) {
      alert('Please describe your symptoms');
      return;
    }

    setIsLoading(true);
    try {
      const response = await consultationService.createConsultation({
        symptoms,
        language: language.toLowerCase(),
        urgency_level: urgencyLevel,
      });

      if (response.success && response.data) {
        setConsultation(response.data);
        await loadMessages(response.data.id);
      } else {
        alert('Failed to start consultation: ' + (response.message || 'Unknown error'));
      }
    } catch (error) {
      console.error('Error starting consultation:', error);
      alert('Failed to start consultation');
    } finally {
      setIsLoading(false);
    }
  };

  const loadMessages = async (consultationId: string) => {
    try {
      const response = await consultationService.getMessages(consultationId);
      if (response.success && response.data) {
        setMessages(response.data.results || response.data);
      }
    } catch (error) {
      console.error('Error loading messages:', error);
    }
  };

  const sendMessage = async () => {
    if (!currentMessage.trim() || !consultation) return;

    const messageText = currentMessage.trim();
    setCurrentMessage('');
    setIsLoading(true);

    try {
      const response = await consultationService.sendMessage(consultation.id, messageText);
      if (response.success) {
        await loadMessages(consultation.id);
      } else {
        alert('Failed to send message: ' + (response.message || 'Unknown error'));
      }
    } catch (error) {
      console.error('Error sending message:', error);
      alert('Failed to send message');
    } finally {
      setIsLoading(false);
    }
  };

  const endConsultation = async () => {
    if (!consultation) return;

    try {
      const response = await consultationService.endConsultation(consultation.id);
      if (response.success) {
        setConsultation(null);
        setMessages([]);
        setSymptoms('');
      } else {
        alert('Failed to end consultation: ' + (response.message || 'Unknown error'));
      }
    } catch (error) {
      console.error('Error ending consultation:', error);
      alert('Failed to end consultation');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  if (!consultation) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-6">
        {/* Header */}
        <div className="max-w-2xl mx-auto mb-6">
          <div className="flex justify-between items-center bg-white rounded-lg p-4 shadow-sm">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                <span className="text-white font-medium text-sm">
                  {user?.first_name?.[0]}{user?.last_name?.[0]}
                </span>
              </div>
              <div>
                <p className="font-medium text-gray-900">{user?.first_name} {user?.last_name}</p>
                <p className="text-sm text-gray-500">{user?.email}</p>
              </div>
            </div>
            <button
              onClick={logout}
              className="text-gray-500 hover:text-gray-700 text-sm"
            >
              Sign Out
            </button>
          </div>
        </div>

        <div className="max-w-2xl mx-auto">
          <div className="bg-white rounded-xl shadow-lg p-8">
            <div className="text-center mb-8">
              <h1 className="text-3xl font-bold text-gray-900 mb-2">AI Health Consultation</h1>
              <p className="text-gray-600">Describe your symptoms to get personalized health advice</p>
            </div>

            <div className="space-y-6">
              <div>
                <label htmlFor="symptoms" className="block text-sm font-medium text-gray-700 mb-2">
                  Describe your symptoms
                </label>
                <textarea
                  id="symptoms"
                  rows={4}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Please describe your symptoms in detail..."
                  value={symptoms}
                  onChange={(e) => setSymptoms(e.target.value)}
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label htmlFor="language" className="block text-sm font-medium text-gray-700 mb-2">
                    Language
                  </label>
                  <select
                    id="language"
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    value={language}
                    onChange={(e) => setLanguage(e.target.value)}
                  >
                    <option value="English">English</option>
                    <option value="Luganda">Luganda</option>
                  </select>
                </div>

                <div>
                  <label htmlFor="urgency" className="block text-sm font-medium text-gray-700 mb-2">
                    Urgency Level
                  </label>
                  <select
                    id="urgency"
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    value={urgencyLevel}
                    onChange={(e) => setUrgencyLevel(e.target.value)}
                  >
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                    <option value="emergency">Emergency</option>
                  </select>
                </div>
              </div>

              <button
                onClick={startConsultation}
                disabled={isLoading || !symptoms.trim()}
                className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
              >
                {isLoading ? 'Starting Consultation...' : 'Start Consultation'}
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-6">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-xl shadow-lg overflow-hidden">
          {/* Header */}
          <div className="bg-blue-600 text-white p-6">
            <div className="flex justify-between items-center">
              <div>
                <h1 className="text-2xl font-bold">Health Consultation</h1>
                <p className="text-blue-100">Status: {consultation.status} | Language: {consultation.language}</p>
              </div>
              <button
                onClick={endConsultation}
                className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg transition-colors"
              >
                End Consultation
              </button>
            </div>
          </div>

          {/* Messages */}
          <div className="h-96 overflow-y-auto p-6 space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.is_ai_response ? 'justify-start' : 'justify-end'}`}
              >
                <div
                  className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${message.is_ai_response
                      ? 'bg-gray-100 text-gray-900'
                      : 'bg-blue-600 text-white'
                    }`}
                >
                  <p className="text-sm">{message.message}</p>
                  <p className={`text-xs mt-1 ${message.is_ai_response ? 'text-gray-500' : 'text-blue-100'
                    }`}>
                    {new Date(message.created_at).toLocaleTimeString()}
                  </p>
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="border-t border-gray-200 p-6">
            <div className="flex space-x-4">
              <input
                type="text"
                placeholder="Type your message..."
                className="flex-1 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                value={currentMessage}
                onChange={(e) => setCurrentMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                disabled={isLoading}
              />
              <button
                onClick={sendMessage}
                disabled={!currentMessage.trim() || isLoading}
                className="bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
              >
                {isLoading ? 'Sending...' : 'Send'}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function ConsultationPage() {
  return (
    <ProtectedRoute>
      <ConsultationPageContent />
    </ProtectedRoute>
  );
}
