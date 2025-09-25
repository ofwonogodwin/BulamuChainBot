'use client';

import React, { useState, useEffect, useRef } from 'react';
import {
    Mic,
    MicOff,
    Volume2,
    VolumeX,
    Send,
    ArrowLeft,
    Loader2,
    Globe
} from 'lucide-react';
import Link from 'next/link';

interface Message {
    id: string;
    text: string;
    sender: 'user' | 'bot';
    timestamp: Date;
    language: string;
    audioUrl?: string;
}

export default function VoiceConsultationPage() {
    const [messages, setMessages] = useState<Message[]>([]);
    const [isListening, setIsListening] = useState(false);
    const [isProcessing, setIsProcessing] = useState(false);
    const [isSpeaking, setIsSpeaking] = useState(false);
    const [currentLanguage, setCurrentLanguage] = useState('en');
    const [textInput, setTextInput] = useState('');
    const [audioEnabled, setAudioEnabled] = useState(true);

    const recognitionRef = useRef<any>(null);
    const synthesisRef = useRef<SpeechSynthesis | null>(null);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const languages = [
        { code: 'en', name: 'English', flag: '🇺🇸', voice: 'en-US' },
        { code: 'lg', name: 'Luganda', flag: '🇺🇬', voice: 'en-US' }, // Fallback to English voice
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
                handleSendMessage(transcript, true);
            };

            recognitionRef.current.onerror = (event: any) => {
                console.error('Speech recognition error:', event.error);
                setIsListening(false);
            };
        }

        // Scroll to bottom when new messages arrive
        scrollToBottom();
    }, [messages]);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

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

    const speakText = (text: string, language: string) => {
        if (!audioEnabled || !synthesisRef.current) return;

        // Stop any current speech
        synthesisRef.current.cancel();

        const utterance = new SpeechSynthesisUtterance(text);
        const langConfig = languages.find(l => l.code === language);
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

    const handleSendMessage = async (text: string, isVoice: boolean = false) => {
        if (!text.trim() || isProcessing) return;

        const userMessage: Message = {
            id: Date.now().toString(),
            text: text.trim(),
            sender: 'user',
            timestamp: new Date(),
            language: currentLanguage
        };

        setMessages(prev => [...prev, userMessage]);
        setTextInput('');
        setIsProcessing(true);

        try {
            // Simulate AI response (replace with actual API call)
            await new Promise(resolve => setTimeout(resolve, 1500));

            // Generate bot response based on symptoms
            const botResponse = generateHealthResponse(text.trim(), currentLanguage);

            const botMessage: Message = {
                id: (Date.now() + 1).toString(),
                text: botResponse,
                sender: 'bot',
                timestamp: new Date(),
                language: currentLanguage
            };

            setMessages(prev => [...prev, botMessage]);

            // Speak the response if audio is enabled
            if (audioEnabled) {
                speakText(botResponse, currentLanguage);
            }

        } catch (error) {
            console.error('Error processing message:', error);
            const errorMessage: Message = {
                id: (Date.now() + 1).toString(),
                text: 'Sorry, I encountered an error. Please try again.',
                sender: 'bot',
                timestamp: new Date(),
                language: currentLanguage
            };
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setIsProcessing(false);
        }
    };

    const generateHealthResponse = (symptoms: string, language: string): string => {
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

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 flex flex-col">
            {/* Header */}
            <header className="bg-white/90 backdrop-blur-sm border-b border-gray-200/50 p-4">
                <div className="max-w-4xl mx-auto flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                        <Link
                            href="/"
                            className="flex items-center space-x-2 text-gray-600 hover:text-gray-800 transition-colors"
                        >
                            <ArrowLeft className="h-5 w-5" />
                            <span className="font-medium">Back to Home</span>
                        </Link>
                    </div>

                    <div className="flex items-center space-x-4">
                        {/* Language Selector */}
                        <select
                            value={currentLanguage}
                            onChange={(e) => setCurrentLanguage(e.target.value)}
                            className="bg-white border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                        >
                            {languages.map((lang) => (
                                <option key={lang.code} value={lang.code}>
                                    {lang.flag} {lang.name}
                                </option>
                            ))}
                        </select>

                        {/* Audio Toggle */}
                        <button
                            onClick={() => {
                                setAudioEnabled(!audioEnabled);
                                if (!audioEnabled) stopSpeaking();
                            }}
                            className={`p-2 rounded-lg transition-colors ${audioEnabled
                                    ? 'bg-blue-100 text-blue-600 hover:bg-blue-200'
                                    : 'bg-gray-100 text-gray-400 hover:bg-gray-200'
                                }`}
                        >
                            {audioEnabled ? <Volume2 className="h-5 w-5" /> : <VolumeX className="h-5 w-5" />}
                        </button>
                    </div>
                </div>
            </header>

            {/* Chat Area */}
            <div className="flex-1 max-w-4xl mx-auto w-full flex flex-col p-4">
                <div className="flex-1 bg-white/95 backdrop-blur-sm rounded-2xl shadow-xl border border-gray-200/50 flex flex-col overflow-hidden">
                    {/* Messages */}
                    <div className="flex-1 overflow-y-auto p-6 space-y-4">
                        {messages.length === 0 && (
                            <div className="text-center py-12">
                                <Mic className="h-16 w-16 text-blue-300 mx-auto mb-4" />
                                <h3 className="text-xl font-semibold text-gray-800 mb-2">
                                    Voice Health Assistant
                                </h3>
                                <p className="text-gray-600">
                                    Tap the microphone or type to describe your symptoms
                                </p>
                            </div>
                        )}

                        {messages.map((message) => (
                            <div
                                key={message.id}
                                className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                            >
                                <div
                                    className={`max-w-xs lg:max-w-md px-4 py-3 rounded-2xl ${message.sender === 'user'
                                            ? 'bg-blue-600 text-white'
                                            : 'bg-gray-100 text-gray-800'
                                        }`}
                                >
                                    <p className="text-sm leading-relaxed">{message.text}</p>
                                    <p className={`text-xs mt-1 ${message.sender === 'user' ? 'text-blue-100' : 'text-gray-500'
                                        }`}>
                                        {message.timestamp.toLocaleTimeString()}
                                    </p>
                                </div>
                            </div>
                        ))}

                        {isProcessing && (
                            <div className="flex justify-start">
                                <div className="bg-gray-100 px-4 py-3 rounded-2xl">
                                    <div className="flex items-center space-x-2">
                                        <Loader2 className="h-4 w-4 animate-spin text-blue-600" />
                                        <span className="text-sm text-gray-600">Thinking...</span>
                                    </div>
                                </div>
                            </div>
                        )}

                        <div ref={messagesEndRef} />
                    </div>

                    {/* Input Area */}
                    <div className="p-6 border-t border-gray-200/50">
                        <div className="flex items-center space-x-4">
                            {/* Voice Input Button */}
                            <button
                                onClick={isListening ? stopListening : startListening}
                                disabled={isProcessing}
                                className={`p-4 rounded-full transition-all duration-200 ${isListening
                                        ? 'bg-red-500 text-white animate-pulse'
                                        : 'bg-blue-600 text-white hover:bg-blue-700'
                                    } ${isProcessing ? 'opacity-50 cursor-not-allowed' : ''}`}
                            >
                                {isListening ? <MicOff className="h-6 w-6" /> : <Mic className="h-6 w-6" />}
                            </button>

                            {/* Text Input */}
                            <div className="flex-1 relative">
                                <input
                                    type="text"
                                    value={textInput}
                                    onChange={(e) => setTextInput(e.target.value)}
                                    onKeyPress={(e) => e.key === 'Enter' && handleSendMessage(textInput)}
                                    placeholder={
                                        currentLanguage === 'lg'
                                            ? 'Nnyonyola obubonero bwo...'
                                            : currentLanguage === 'sw'
                                                ? 'Elezea dalili zako...'
                                                : 'Describe your symptoms...'
                                    }
                                    className="w-full p-4 pr-12 border border-gray-300 rounded-2xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                    disabled={isProcessing || isListening}
                                />

                                {/* Send Button */}
                                <button
                                    onClick={() => handleSendMessage(textInput)}
                                    disabled={!textInput.trim() || isProcessing || isListening}
                                    className="absolute right-2 top-1/2 transform -translate-y-1/2 p-2 bg-blue-600 text-white rounded-full hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                                >
                                    <Send className="h-4 w-4" />
                                </button>
                            </div>

                            {/* Speaking Indicator */}
                            {isSpeaking && (
                                <button
                                    onClick={stopSpeaking}
                                    className="p-4 bg-green-500 text-white rounded-full animate-pulse"
                                >
                                    <Volume2 className="h-6 w-6" />
                                </button>
                            )}
                        </div>

                        {/* Status Indicators */}
                        <div className="flex items-center justify-center mt-4 space-x-6 text-sm text-gray-500">
                            {isListening && (
                                <div className="flex items-center space-x-2">
                                    <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
                                    <span>Listening...</span>
                                </div>
                            )}

                            {isSpeaking && (
                                <div className="flex items-center space-x-2">
                                    <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                                    <span>Speaking...</span>
                                </div>
                            )}

                            <div className="flex items-center space-x-2">
                                <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                                <span>
                                    {languages.find(l => l.code === currentLanguage)?.name} Mode
                                </span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
