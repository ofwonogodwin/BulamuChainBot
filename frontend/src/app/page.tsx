'use client';

import React, { useState, useEffect } from 'react';
import {
  Send,
  Volume2,
  VolumeX,
  Stethoscope,
  Plus,
  Trash2,
  Mic,
  Activity,
  Shield,
  BookOpen
} from 'lucide-react';
import Link from 'next/link';

import Navigation from '@/components/Navigation';
import { useAuth } from '@/contexts/AuthContext';
import { useLanguage } from '@/contexts/LanguageContext';
import { consultationService } from '@/services/api';

interface ChatMessage {
  id: string;
  content: string;
  isUser: boolean;
  timestamp: Date;
}

interface Chat {
  id: string;
  title: string;
  messages: ChatMessage[];
  createdAt: Date;
}

export default function HomePage() {
  const [message, setMessage] = useState('');
  const [audioEnabled, setAudioEnabled] = useState(true);
  const [chats, setChats] = useState<Chat[]>([]);
  const [activeChat, setActiveChat] = useState<Chat | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const { isAuthenticated, logout, user } = useAuth();
  const { getPlaceholderText, getGreetingText, getCurrentLanguageData } = useLanguage();

  // Load user's chat data from localStorage
  useEffect(() => {
    if (isAuthenticated && user) {
      const savedChats = localStorage.getItem(`chats_${user.id || user.email}`);
      if (savedChats) {
        try {
          const parsedChats = JSON.parse(savedChats).map((chat: Chat & { createdAt: string; messages: Array<ChatMessage & { timestamp: string }> }) => ({
            ...chat,
            createdAt: new Date(chat.createdAt),
            messages: chat.messages.map((msg: ChatMessage & { timestamp: string }) => ({
              ...msg,
              timestamp: new Date(msg.timestamp)
            }))
          }));
          setChats(parsedChats);
        } catch (error) {
          console.error('Error loading chats:', error);
        }
      }
    } else {
      // Clear chats when user logs out
      setChats([]);
      setActiveChat(null);
    }
  }, [isAuthenticated, user]);

  // Save chats to localStorage whenever chats change
  useEffect(() => {
    if (isAuthenticated && user && chats.length > 0) {
      localStorage.setItem(`chats_${user.id || user.email}`, JSON.stringify(chats));
    }
  }, [chats, isAuthenticated, user]);

  const createNewChat = () => {
    const newChat: Chat = {
      id: Date.now().toString(),
      title: 'New Conversation',
      messages: [],
      createdAt: new Date()
    };
    setChats([newChat, ...chats]);
    setActiveChat(newChat);
  };

  const generateChatTitle = (firstMessage: string): string => {
    // Generate a meaningful title from the first message
    const cleanMessage = firstMessage.trim();
    if (cleanMessage.length <= 30) {
      return cleanMessage;
    }

    // Try to find a good break point
    const words = cleanMessage.split(' ');
    let title = '';
    for (const word of words) {
      if ((title + ' ' + word).length <= 30) {
        title += (title ? ' ' : '') + word;
      } else {
        break;
      }
    }

    // Add ellipsis if truncated
    return title + (title.length < cleanMessage.length ? '...' : '');
  };

  const deleteChat = (chatId: string) => {
    setChats(chats.filter(chat => chat.id !== chatId));
    if (activeChat?.id === chatId) {
      setActiveChat(null);
    }
  };

  const sendMessage = async () => {
    if (!message.trim() || isLoading) return;

    let currentChat = activeChat;

    // If no active chat, create one
    if (!currentChat) {
      currentChat = {
        id: Date.now().toString(),
        title: generateChatTitle(message),
        messages: [],
        createdAt: new Date()
      };
      setChats([currentChat, ...chats]);
      setActiveChat(currentChat);
    }

    // Add user message
    const userMessage: ChatMessage = {
      id: Date.now().toString() + '_user',
      content: message,
      isUser: true,
      timestamp: new Date()
    };

    const updatedMessages = [...currentChat.messages, userMessage];

    // Update chat with user message
    const updatedChat = { ...currentChat, messages: updatedMessages };
    const updatedChats = chats.map(chat => chat.id === currentChat!.id ? updatedChat : chat);
    setChats(updatedChats);
    setActiveChat(updatedChat);

    const currentMessage = message;
    setMessage('');
    setIsLoading(true);

    try {
      // Get conversation history for context
      const conversationHistory = updatedMessages.slice(-10).map(msg => ({
        content: msg.content,
        isUser: msg.isUser
      }));

      // Call the AI service with Gemini
      const response = await consultationService.chatWithAI({
        message: currentMessage,
        language: getCurrentLanguageData().code,
        conversation_history: conversationHistory
      });

      if (response.success && response.data) {
        const aiMessage: ChatMessage = {
          id: Date.now().toString() + '_ai',
          content: response.data.response || response.data.message,
          isUser: false,
          timestamp: new Date()
        };

        const finalMessages = [...updatedMessages, aiMessage];
        const finalChat = { ...updatedChat, messages: finalMessages };

        const finalChats = chats.map(chat =>
          chat.id === currentChat!.id ? finalChat : chat
        );
        setChats(finalChats);
        setActiveChat(finalChat);
      } else {
        // Fallback to local response if API fails
        const fallbackResponse = generateFallbackResponse(currentMessage, getCurrentLanguageData().code);

        const aiMessage: ChatMessage = {
          id: Date.now().toString() + '_ai',
          content: fallbackResponse,
          isUser: false,
          timestamp: new Date()
        };

        const finalMessages = [...updatedMessages, aiMessage];
        const finalChat = { ...updatedChat, messages: finalMessages };

        const finalChats = chats.map(chat =>
          chat.id === currentChat!.id ? finalChat : chat
        );
        setChats(finalChats);
        setActiveChat(finalChat);
      }
    } catch (error) {
      console.error('Error getting AI response:', error);

      // Fallback to local response on error
      const fallbackResponse = generateFallbackResponse(currentMessage, getCurrentLanguageData().code);

      const aiMessage: ChatMessage = {
        id: Date.now().toString() + '_ai',
        content: fallbackResponse,
        isUser: false,
        timestamp: new Date()
      };

      const finalMessages = [...updatedMessages, aiMessage];
      const finalChat = { ...updatedChat, messages: finalMessages };

      const finalChats = chats.map(chat =>
        chat.id === currentChat!.id ? finalChat : chat
      );
      setChats(finalChats);
      setActiveChat(finalChat);
    } finally {
      setIsLoading(false);
    }
  }; const generateFallbackResponse = (symptoms: string, language: string): string => {
    const responses = {
      en: {
        fever: "Based on your fever symptoms, I recommend: 1) Rest and stay hydrated 2) Take paracetamol for fever 3) Monitor your temperature 4) See a doctor if fever persists over 3 days or exceeds 39°C. If you experience difficulty breathing or severe symptoms, seek immediate medical attention.",
        headache: "For headache relief: 1) Rest in a quiet, dark room 2) Apply cold compress to forehead 3) Stay hydrated 4) Take paracetamol if needed 5) See a doctor if headaches are severe, frequent, or accompanied by vision changes.",
        stomach: "For stomach pain: 1) Eat bland foods (rice, bananas) 2) Stay hydrated with small sips of water 3) Avoid dairy and spicy foods 4) Rest 5) Seek medical help if pain is severe, you have blood in stool, or persistent vomiting.",
        default: "Thank you for describing your symptoms. While I can provide general guidance, it's important to consult with a healthcare professional for proper diagnosis and treatment. Based on what you've shared, I recommend monitoring your symptoms and seeking medical attention if they worsen or persist."
      },
      lg: {
        fever: "Ku busagwa bw'omusujja: 1) Wummulire era nywa amazzi mangi 2) Mira panadol ku musujja 3) Kebera obupya bw'omubiri gwo 4) Laba omusawo singa omusujja gubeerera ennaku ssatu oba gusukka ku 39°C.",
        headache: "Ku mutwe ogulumwa: 1) Wummulire mu kifo ekisiriikirira 2) Teeka ekicaaye ku kyenyi 3) Nywa amazzi mangi 4) Mira panadol singa kyetaagisa 5) Laba omusawo singa omutwe gulumya nnyo.",
        stomach: "Ku lubuto olulumwa: 1) Lya mmere ez'eetegese (empuuta, gonja) 2) Nywa amazzi gatono gatono 3) Weekweke amata n'emmere ezilimu obubbaane 4) Wummulire 5) Noonya obujjanjabi singa obulumi bungi nnyo.",
        default: "Webale okunyonyola obubonero bwo. Newankubadde nsobola okukuwa amagezi ag'okutandikira, kikulu olabe omusawo omukugu okufuna obujjanjabi obututuufu."
      },
      sw: {
        fever: "Kwa dalili za homa: 1) Pumzika na kunywa maji mengi 2) Tumia panadol kwa homa 3) Fuatilia joto la mwili 4) Ona daktari ikiwa homa inaendelea kwa siku tatu au inazidi 39°C.",
        headache: "Kwa maumivu ya kichwa: 1) Pumzika katika chumba kimya na chenye giza 2) Weka kitu cha baridi kwenye paji 3) Nywa maji mengi 4) Tumia panadol ikihitajika 5) Ona daktari ikiwa maumivu ni makali.",
        stomach: "Kwa maumivu ya tumbo: 1) Kula chakula rahisi (mchele, ndizi) 2) Nywa maji kidogo kidogo 3) Epuka maziwa na chakula chenye bizari 4) Pumzika 5) Tafuta msaada wa kimatibabu ikiwa maumivu ni makali.",
        default: "Asante kwa kuelezea dalili zako. Ingawa ninaweza kutoa mwongozo wa jumla, ni muhimu kuona mtaalamu wa afya kwa uchunguzi na matibabu sahihi."
      }
    };

    const langResponses = responses[language as keyof typeof responses] || responses.en;
    const lowerSymptoms = symptoms.toLowerCase();

    if (lowerSymptoms.includes('fever') || lowerSymptoms.includes('omusujja') || lowerSymptoms.includes('homa')) {
      return langResponses.fever;
    } else if (lowerSymptoms.includes('headache') || lowerSymptoms.includes('mutwe') || lowerSymptoms.includes('kichwa')) {
      return langResponses.headache;
    } else if (lowerSymptoms.includes('stomach') || lowerSymptoms.includes('lubuto') || lowerSymptoms.includes('tumbo')) {
      return langResponses.stomach;
    }

    return langResponses.default;
  };

  const stopSpeaking = () => {
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      window.speechSynthesis.cancel();
    }
  };
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 flex">
      {/* Navigation Component */}
      <Navigation />

      {/* Side Panel */}
      <div className="w-80 bg-white/90 backdrop-blur-sm border-r border-gray-200 flex flex-col">
        {/* Side Panel Header */}
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-800">Chats</h2>
            <button
              onClick={createNewChat}
              className="p-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              title="New Chat"
            >
              <Plus className="h-4 w-4" />
            </button>
          </div>

          {/* Auth buttons for non-authenticated users */}
          {!isAuthenticated && (
            <div className="flex flex-col space-y-2">
              <Link
                href="/login"
                className="text-center bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors text-sm"
              >
                Sign In
              </Link>
              <Link
                href="/register"
                className="text-center bg-white text-blue-600 border border-blue-600 px-4 py-2 rounded-lg hover:bg-blue-50 transition-colors text-sm"
              >
                Get Started
              </Link>
            </div>
          )}

          {/* Welcome message for authenticated users */}
          {isAuthenticated && user && (
            <div className="mb-3 p-2 bg-blue-50 rounded-lg border border-blue-200">
              <p className="text-sm font-medium text-blue-800">
                Welcome, {user.first_name || user.email?.split('@')[0] || 'User'}! 👋
              </p>
            </div>
          )}

          {/* User info for authenticated users */}
          {isAuthenticated && user && (
            <div className="flex items-center space-x-2 p-2 bg-gray-50 rounded-lg">
              <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                <span className="text-white font-medium text-xs">
                  {user.first_name?.[0]?.toUpperCase() || user.email?.[0]?.toUpperCase() || 'U'}
                  {user.last_name?.[0]?.toUpperCase() || ''}
                </span>
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">
                  {user.first_name ? `${user.first_name} ${user.last_name || ''}`.trim() : user.email}
                </p>
                <p className="text-xs text-gray-500 truncate">
                  {chats.length} conversation{chats.length !== 1 ? 's' : ''}
                </p>
              </div>
              <button
                onClick={logout}
                className="text-xs text-red-600 hover:text-red-800"
              >
                Logout
              </button>
            </div>
          )}
        </div>

        {/* Chat History */}
        <div className="flex-1 overflow-y-auto p-4 space-y-2">
          {chats.map((chat) => (
            <div
              key={chat.id}
              className={`p-3 rounded-lg cursor-pointer transition-colors group ${activeChat?.id === chat.id
                ? 'bg-blue-100 border border-blue-300'
                : 'bg-gray-50 hover:bg-gray-100'
                }`}
              onClick={() => setActiveChat(chat)}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate mb-1">
                    {chat.title}
                  </p>
                  <div className="flex items-center space-x-2 text-xs text-gray-500">
                    <span>{chat.messages.length} messages</span>
                    <span>•</span>
                    <span>{chat.createdAt.toLocaleDateString()}</span>
                  </div>
                  {chat.messages.length > 0 && (
                    <p className="text-xs text-gray-400 mt-1 truncate">
                      {chat.messages[chat.messages.length - 1].content.substring(0, 40)}
                      {chat.messages[chat.messages.length - 1].content.length > 40 ? '...' : ''}
                    </p>
                  )}
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    deleteChat(chat.id);
                  }}
                  className="opacity-0 group-hover:opacity-100 p-1 text-red-500 hover:text-red-700 transition-all flex-shrink-0"
                  title="Delete Chat"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            </div>
          ))}

          {chats.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              <Stethoscope className="h-12 w-12 mx-auto mb-3 text-gray-300" />
              <p className="text-sm">No conversations yet</p>
              <p className="text-xs">Start a new chat to get help</p>
            </div>
          )}
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Top Controls */}
        <div className="p-4 border-b border-gray-200 bg-white/90 backdrop-blur-sm">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="bg-blue-600 p-2 rounded-lg">
                <Stethoscope className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-800">BulamuChainBot</h1>
                <p className="text-sm text-blue-600">{getGreetingText()}</p>
              </div>
            </div>

            <div className="flex items-center space-x-2">
              <button
                onClick={() => {
                  setAudioEnabled(!audioEnabled);
                  if (!audioEnabled) stopSpeaking();
                }}
                className={`p-2 rounded-lg transition-colors ${audioEnabled
                  ? 'bg-blue-100 text-blue-600 hover:bg-blue-200'
                  : 'bg-gray-100 text-gray-400 hover:bg-gray-200'
                  }`}
                title={audioEnabled ? 'Disable Audio' : 'Enable Audio'}
              >
                {audioEnabled ? <Volume2 className="h-4 w-4" /> : <VolumeX className="h-4 w-4" />}
              </button>
            </div>
          </div>
        </div>

        {/* Chat Messages */}
        <div className="flex-1 overflow-y-auto p-6">
          {activeChat ? (
            <div className="space-y-4 max-w-4xl mx-auto">
              {/* Back to Main Page Button */}
              <div className="mb-6">
                <button
                  onClick={() => setActiveChat(null)}
                  className="flex items-center space-x-2 text-blue-600 hover:text-blue-800 transition-colors bg-white rounded-lg px-4 py-2 shadow-sm hover:shadow-md border border-blue-200"
                >
                  <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                  </svg>
                  <span className="text-sm font-medium">Back to Main Page</span>
                </button>
              </div>

              {activeChat.messages.map((msg) => (
                <div
                  key={msg.id}
                  className={`flex ${msg.isUser ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-xs lg:max-w-md px-4 py-3 rounded-2xl ${msg.isUser
                      ? 'bg-blue-600 text-white rounded-br-md'
                      : 'bg-gray-100 text-gray-900 rounded-bl-md'
                      }`}
                  >
                    <p className="text-sm">{msg.content}</p>
                    <p className={`text-xs mt-1 ${msg.isUser ? 'text-blue-100' : 'text-gray-500'
                      }`}>
                      {msg.timestamp.toLocaleTimeString()}
                    </p>
                  </div>
                </div>
              ))}

              {/* AI Thinking Indicator */}
              {isLoading && (
                <div className="flex justify-start">
                  <div className="max-w-xs lg:max-w-md px-4 py-3 rounded-2xl bg-gray-100 text-gray-900 rounded-bl-md">
                    <div className="flex items-center space-x-2">
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                      </div>
                      <span className="text-xs text-gray-500">AI is thinking...</span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="flex-1 flex items-center justify-center">
              <div className="text-center max-w-2xl mx-auto">
                <div className="bg-blue-600 p-8 rounded-full inline-block mb-6 shadow-lg">
                  <Stethoscope className="h-16 w-16 text-white" />
                </div>
                <h2 className="text-2xl font-bold text-gray-800 mb-3">
                  BulamuChainBot
                </h2>
                <p className="text-gray-600 mb-4">
                  AI-powered health assistant improving healthcare access for rural
                </p>
                <p className="text-gray-600 mb-6">
                  and underserved Ugandans
                </p>

                <p className="text-blue-600 font-semibold text-center mb-8">
                  Health that Talks, Records that Last
                </p>

                {/* Feature Cards Container */}
                <div className="bg-white/95 backdrop-blur-sm rounded-2xl shadow-xl border border-gray-200/50 p-4 mb-8">
                  <div className="flex items-center justify-between">
                    <Link
                      href="/voice-consultation"
                      className="group flex items-center space-x-2 p-2 rounded-xl hover:bg-gray-50 transition-all duration-200 flex-1 justify-center"
                    >
                      <div className="flex items-center justify-center w-8 h-8 bg-blue-50 rounded-full group-hover:bg-blue-100 transition-colors">
                        <Mic className="h-3 w-3 text-blue-600" />
                      </div>
                      <span className="text-xs font-medium text-gray-600 group-hover:text-gray-800">
                        Voice Chat
                      </span>
                      <div className="px-1 py-0.5 rounded-full text-[8px] font-bold bg-green-500 text-white">
                        New
                      </div>
                    </Link>

                    <Link
                      href="/emergency"
                      className="group flex items-center space-x-2 p-2 rounded-xl hover:bg-gray-50 transition-all duration-200 flex-1 justify-center"
                    >
                      <div className="flex items-center justify-center w-8 h-8 bg-red-50 rounded-full group-hover:bg-red-100 transition-colors">
                        <Activity className="h-3 w-3 text-red-600" />
                      </div>
                      <span className="text-xs font-medium text-gray-600 group-hover:text-gray-800">
                        Emergency
                      </span>
                      <div className="px-1 py-0.5 rounded-full text-[8px] font-bold bg-red-500 text-white">
                        Critical
                      </div>
                    </Link>

                    <Link
                      href="/blockchain"
                      className="group flex items-center space-x-2 p-2 rounded-xl hover:bg-gray-50 transition-all duration-200 flex-1 justify-center"
                    >
                      <div className="flex items-center justify-center w-8 h-8 bg-green-50 rounded-full group-hover:bg-green-100 transition-colors">
                        <Shield className="h-3 w-3 text-green-600" />
                      </div>
                      <span className="text-xs font-medium text-gray-600 group-hover:text-gray-800">
                        Blockchain
                      </span>
                    </Link>

                    <Link
                      href="/education"
                      className="group flex items-center space-x-2 p-2 rounded-xl hover:bg-gray-50 transition-all duration-200 flex-1 justify-center"
                    >
                      <div className="flex items-center justify-center w-8 h-8 bg-purple-50 rounded-full group-hover:bg-purple-100 transition-colors">
                        <BookOpen className="h-3 w-3 text-purple-600" />
                      </div>
                      <span className="text-xs font-medium text-gray-600 group-hover:text-gray-800">
                        Education
                      </span>
                    </Link>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Message Input */}
        <div className="p-4 border-t border-gray-200 bg-white/90 backdrop-blur-sm">
          <div className="max-w-4xl mx-auto">
            <div className="flex items-end space-x-4">
              <div className="flex-1 relative">
                <textarea
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  placeholder={getPlaceholderText()}
                  className="w-full p-4 pr-12 border border-gray-300 rounded-2xl resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent max-h-32 text-black"
                  rows={1}
                  onKeyPress={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault();
                      sendMessage();
                    }
                  }}
                />
                <div className="absolute bottom-2 right-2 text-xs text-gray-400">
                  {message.length}/500
                </div>
              </div>
              <button
                onClick={sendMessage}
                disabled={!message.trim() || isLoading}
                className="p-3 bg-blue-600 text-white rounded-full hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                title={isLoading ? "AI is thinking..." : "Send Message"}
              >
                {isLoading ? (
                  <div className="animate-spin h-5 w-5 border-2 border-white border-t-transparent rounded-full" />
                ) : (
                  <Send className="h-5 w-5" />
                )}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
