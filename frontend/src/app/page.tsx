'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Stethoscope, Mic, MicOff, Volume2, VolumeX, Globe, Send } from 'lucide-react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import Navigation from '@/components/Navigation';

export default function HomePage() {
  const [message, setMessage] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [currentLanguage, setCurrentLanguage] = useState('en');
  const [audioEnabled, setAudioEnabled] = useState(true);

  const router = useRouter();
  const recognitionRef = useRef<any>(null);
  const synthesisRef = useRef<SpeechSynthesis | null>(null);

  const languages = [
    { code: 'en', name: 'English', flag: '🇺🇸', voice: 'en-US' },
    { code: 'lg', name: 'Luganda', flag: '🇺🇬', voice: 'en-US' },
    { code: 'sw', name: 'Swahili', flag: '🇰🇪', voice: 'sw-KE' }
  ];

  useEffect(() => {
    // Initialize speech synthesis
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      synthesisRef.current = window.speechSynthesis;
    }

    // Initialize speech recognition
    if (typeof window !== 'undefined' && ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)) {
      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();

      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = false;
      recognitionRef.current.lang = currentLanguage === 'en' ? 'en-US' : currentLanguage === 'sw' ? 'sw-KE' : 'en-US';

      recognitionRef.current.onstart = () => {
        setIsListening(true);
      };

      recognitionRef.current.onend = () => {
        setIsListening(false);
      };

      recognitionRef.current.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        setMessage(transcript);
      };

      recognitionRef.current.onerror = (event: any) => {
        console.error('Speech recognition error:', event.error);
        setIsListening(false);
      };
    }
  }, [currentLanguage]);

  const startListening = () => {
    if (recognitionRef.current && !isListening) {
      try {
        recognitionRef.current.start();
      } catch (error) {
        console.error('Error starting speech recognition:', error);
      }
    }
  };

  const stopListening = () => {
    if (recognitionRef.current && isListening) {
      recognitionRef.current.stop();
    }
  };

  const speakText = (text: string) => {
    if (!audioEnabled || !synthesisRef.current || !text.trim()) return;

    synthesisRef.current.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    const langConfig = languages.find(l => l.code === currentLanguage);
    utterance.lang = langConfig?.voice || 'en-US';
    utterance.rate = 0.9;
    utterance.pitch = 1.0;

    utterance.onstart = () => setIsSpeaking(true);
    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = () => setIsSpeaking(false);

    synthesisRef.current.speak(utterance);
  };

  const stopSpeaking = () => {
    if (synthesisRef.current) {
      synthesisRef.current.cancel();
      setIsSpeaking(false);
    }
  };

  const getPlaceholderText = () => {
    switch (currentLanguage) {
      case 'lg': return 'Nnyonyola obubonero bwo oba ebikuluma...';
      case 'sw': return 'Elezea dalili zako au maswali yako ya afya...';
      default: return 'Tell me about your symptoms or health concerns...';
    }
  };
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 flex flex-col relative overflow-hidden">
      {/* Navigation Component */}
      <Navigation />

      {/* Simplified background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute inset-0 bg-gradient-to-br from-blue-50/50 via-transparent to-indigo-50/50"></div>
      </div>
      {/* Main Content - ChatGPT Style */}
      <main className="flex-1 flex flex-col items-center justify-center px-4 py-12 relative">
        {/* Top right controls */}
        <div className="absolute top-6 right-6 flex items-center space-x-4 z-10">
          {/* Language Selector */}
          <div className="relative">
            <select
              value={currentLanguage}
              onChange={(e) => setCurrentLanguage(e.target.value)}
              className="bg-white/90 backdrop-blur-sm border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 appearance-none pr-8"
            >
              {languages.map((lang) => (
                <option key={lang.code} value={lang.code}>
                  {lang.flag} {lang.name}
                </option>
              ))}
            </select>
            <Globe className="absolute right-2 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400 pointer-events-none" />
          </div>

          {/* Audio Toggle */}
          <button
            onClick={() => {
              setAudioEnabled(!audioEnabled);
              if (!audioEnabled) stopSpeaking();
            }}
            className={`p-2 rounded-lg transition-colors backdrop-blur-sm ${audioEnabled
              ? 'bg-blue-100 text-blue-600 hover:bg-blue-200'
              : 'bg-gray-100 text-gray-400 hover:bg-gray-200'
              }`}
            title={audioEnabled ? 'Disable Audio' : 'Enable Audio'}
          >
            {audioEnabled ? <Volume2 className="h-4 w-4" /> : <VolumeX className="h-4 w-4" />}
          </button>

          {/* Auth buttons */}
          <Link
            href="/login"
            className="text-blue-600 hover:text-blue-800 transition-all duration-300 font-medium px-4 py-2 rounded-xl hover:bg-blue-50 transform hover:scale-105 bg-white/90 backdrop-blur-sm"
          >
            Sign In
          </Link>
          <Link
            href="/register"
            className="bg-gradient-to-r from-blue-600 to-blue-700 text-white px-6 py-2.5 rounded-xl hover:from-blue-700 hover:to-blue-800 transition-all duration-300 font-medium shadow-lg hover:shadow-xl transform hover:scale-105"
          >
            Get Started
          </Link>
        </div>
        <div className="w-full max-w-2xl mx-auto text-center">
          {/* Clean Logo */}
          <div className="mb-12">
            <div className="bg-blue-600 p-8 rounded-full inline-block mb-6 shadow-lg">
              <Stethoscope className="h-20 w-20 text-white" />
            </div>
            <h1 className="text-4xl font-bold text-gray-800 mb-3">
              BulamuChainBot
            </h1>
            <p className="text-gray-600 text-lg font-medium">AI Health Assistant for Everyone</p>
          </div>

          {/* Enhanced Input Area with Voice */}
          <div className="bg-white/95 backdrop-blur-sm rounded-3xl shadow-2xl border border-white/20 p-6 mb-6 hover:shadow-3xl transition-all duration-300">
            <div className="relative">
              <textarea
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder={getPlaceholderText()}
                disabled={isListening}
                className="w-full h-24 p-4 pr-16 border-0 bg-gray-50/50 rounded-2xl resize-none focus:outline-none focus:ring-0 focus:bg-white transition-all duration-300 text-gray-800 placeholder-gray-400 text-base leading-relaxed shadow-inner disabled:opacity-50"
                style={{
                  fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif'
                }}
              />

              {/* Send Button */}
              <button
                onClick={() => {
                  if (message.trim()) {
                    sessionStorage.setItem('initialSymptoms', message);
                    router.push('/consultation');
                  }
                }}
                disabled={!message.trim()}
                className="absolute top-4 right-4 p-3 bg-blue-600 text-white rounded-full hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                title="Send Message"
              >
                <Send className="h-4 w-4" />
              </button>

              {/* Character count */}
              <div className="absolute bottom-3 right-4 text-xs text-gray-400">
                {message.length}/500
              </div>

              {/* Voice Status Indicator */}
              {(isListening || isSpeaking) && (
                <div className="absolute bottom-3 left-4 flex items-center space-x-2">
                  {isListening && (
                    <div className="flex items-center space-x-1 text-xs text-red-600">
                      <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
                      <span>Listening...</span>
                    </div>
                  )}
                  {isSpeaking && (
                    <div className="flex items-center space-x-1 text-xs text-green-600">
                      <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                      <span>Speaking...</span>
                    </div>
                  )}
                </div>
              )}
            </div>




          </div>
        </div>
      </main>
    </div>
  );
}
