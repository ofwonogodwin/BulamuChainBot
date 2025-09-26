'use client';

import React, { useState, useEffect } from 'react';
import {
    AlertTriangle,
    Phone,
    MapPin,
    Clock,
    Heart,
    ArrowLeft,
    Check,
    X,
    Loader2
} from 'lucide-react';
import Link from 'next/link';

interface EmergencyAlert {
    id: string;
    severity: 'low' | 'medium' | 'high' | 'critical';
    symptoms: string[];
    recommendation: string;
    actions: string[];
    hotlines: { name: string; number: string; available: string }[];
    timestamp: Date;
}

export default function EmergencyPage() {
    const [symptoms, setSymptoms] = useState('');
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [alert, setAlert] = useState<EmergencyAlert | null>(null);
    const [location, setLocation] = useState<string>('');

    const emergencyHotlines = [
        { name: 'Police Emergency', number: '999', available: '24/7' },
        { name: 'Medical Emergency', number: '911', available: '24/7' },
        { name: 'Mulago Hospital', number: '+256-414-554-000', available: '24/7' },
        { name: 'Case Medical Centre', number: '+256-312-258-100', available: '24/7' },
        { name: 'Kampala Hospital', number: '+256-312-200-400', available: '24/7' }
    ];

    const criticalSymptoms = [
        'chest pain', 'difficulty breathing', 'severe bleeding', 'unconscious',
        'heart attack', 'stroke', 'severe burn', 'poisoning', 'choking',
        'severe allergic reaction', 'broken bone', 'severe head injury'
    ];

    const highSeveritySymptoms = [
        'high fever', 'severe headache', 'vomiting blood', 'severe abdominal pain',
        'difficulty swallowing', 'severe dizziness', 'fainting', 'seizure'
    ];

    useEffect(() => {
        // Get user's location with proper error handling
        const getLocation = () => {
            if (!navigator.geolocation) {
                setLocation('Geolocation not supported by this browser');
                return;
            }

            navigator.geolocation.getCurrentPosition(
                (position) => {
                    // In a real app, you would reverse geocode this to get the address
                    setLocation(`Lat: ${position.coords.latitude.toFixed(4)}, Long: ${position.coords.longitude.toFixed(4)}`);
                },
                (error) => {
                    let errorMessage = 'Location unavailable';
                    
                    switch (error.code) {
                        case error.PERMISSION_DENIED:
                            errorMessage = 'Location access denied by user';
                            break;
                        case error.POSITION_UNAVAILABLE:
                            errorMessage = 'Location information unavailable';
                            break;
                        case error.TIMEOUT:
                            errorMessage = 'Location request timed out';
                            break;
                        default:
                            errorMessage = `Location error: ${error.message}`;
                            break;
                    }
                    
                    console.warn('Geolocation error:', errorMessage);
                    setLocation(errorMessage);
                },
                {
                    enableHighAccuracy: false, // Use less accurate but faster location
                    timeout: 10000, // 10 second timeout
                    maximumAge: 300000 // Accept cached location up to 5 minutes old
                }
            );
        };

        getLocation();
    }, []);

    const analyzeEmergency = async () => {
        if (!symptoms.trim()) return;

        setIsAnalyzing(true);

        try {
            // Simulate analysis delay
            await new Promise(resolve => setTimeout(resolve, 2000));

            const lowerSymptoms = symptoms.toLowerCase();
            let severity: 'low' | 'medium' | 'high' | 'critical' = 'low';
            let recommendation = '';
            let actions: string[] = [];
            let relevantHotlines = [...emergencyHotlines];

            // Check for critical symptoms
            const hasCriticalSymptoms = criticalSymptoms.some(symptom =>
                lowerSymptoms.includes(symptom)
            );

            const hasHighSeveritySymptoms = highSeveritySymptoms.some(symptom =>
                lowerSymptoms.includes(symptom)
            );

            if (hasCriticalSymptoms) {
                severity = 'critical';
                recommendation = 'IMMEDIATE MEDICAL ATTENTION REQUIRED';
                actions = [
                    'Call emergency services immediately (999 or 911)',
                    'Do not move unless absolutely necessary',
                    'Stay calm and follow emergency operator instructions',
                    'Have someone stay with you until help arrives',
                    'If possible, have medical history and medications ready'
                ];
            } else if (hasHighSeveritySymptoms) {
                severity = 'high';
                recommendation = 'Seek urgent medical attention within 1 hour';
                actions = [
                    'Contact nearest hospital or clinic immediately',
                    'Consider calling emergency services if symptoms worsen',
                    'Monitor symptoms closely',
                    'Have someone accompany you to medical facility',
                    'Bring identification and medical information'
                ];
            } else if (lowerSymptoms.includes('fever') || lowerSymptoms.includes('pain')) {
                severity = 'medium';
                recommendation = 'Medical consultation recommended within 24 hours';
                actions = [
                    'Schedule appointment with healthcare provider',
                    'Monitor symptoms and note any changes',
                    'Take basic first aid measures if applicable',
                    'Rest and stay hydrated',
                    'Seek immediate help if symptoms worsen'
                ];
            } else {
                severity = 'low';
                recommendation = 'Monitor symptoms and consider medical consultation';
                actions = [
                    'Keep track of symptoms',
                    'Try basic home remedies if appropriate',
                    'Schedule non-urgent medical appointment if symptoms persist',
                    'Stay hydrated and get adequate rest',
                    'Contact healthcare provider if concerned'
                ];
            }

            const newAlert: EmergencyAlert = {
                id: Date.now().toString(),
                severity,
                symptoms: symptoms.split(',').map(s => s.trim()),
                recommendation,
                actions,
                hotlines: relevantHotlines,
                timestamp: new Date()
            };

            setAlert(newAlert);

        } catch (error) {
            console.error('Error analyzing symptoms:', error);
        } finally {
            setIsAnalyzing(false);
        }
    };

    const getSeverityColor = (severity: string) => {
        switch (severity) {
            case 'critical': return 'text-red-600 bg-red-50 border-red-200';
            case 'high': return 'text-orange-600 bg-orange-50 border-orange-200';
            case 'medium': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
            default: return 'text-blue-600 bg-blue-50 border-blue-200';
        }
    };

    const getSeverityIcon = (severity: string) => {
        switch (severity) {
            case 'critical': return <AlertTriangle className="h-6 w-6 text-red-600" />;
            case 'high': return <AlertTriangle className="h-6 w-6 text-orange-600" />;
            case 'medium': return <Heart className="h-6 w-6 text-yellow-600" />;
            default: return <Heart className="h-6 w-6 text-blue-600" />;
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-red-50 via-white to-orange-50">
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

                    <div className="flex items-center space-x-2">
                        <AlertTriangle className="h-6 w-6 text-red-600" />
                        <span className="font-semibold text-red-600">Emergency Assistant</span>
                    </div>
                </div>
            </header>

            <div className="max-w-4xl mx-auto p-4">
                {!alert ? (
                    /* Input Section */
                    <div className="bg-white/95 backdrop-blur-sm rounded-2xl shadow-xl border border-gray-200/50 p-8 mb-6">
                        <div className="text-center mb-8">
                            <AlertTriangle className="h-16 w-16 text-red-500 mx-auto mb-4" />
                            <h1 className="text-3xl font-bold text-gray-800 mb-2">Emergency Health Assessment</h1>
                            <p className="text-gray-600">
                                Describe your symptoms for immediate risk assessment and guidance
                            </p>
                        </div>

                        <div className="space-y-6">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Describe your symptoms in detail:
                                </label>
                                <textarea
                                    value={symptoms}
                                    onChange={(e) => setSymptoms(e.target.value)}
                                    placeholder="e.g., severe chest pain, difficulty breathing, fever of 39°C..."
                                    className="w-full h-32 p-4 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent resize-none text-black"
                                    rows={4}
                                />
                            </div>

                            {location && (
                                <div className="flex items-center space-x-2 text-sm text-gray-600">
                                    <MapPin className="h-4 w-4" />
                                    <span>Location: {location}</span>
                                </div>
                            )}

                            <button
                                onClick={analyzeEmergency}
                                disabled={!symptoms.trim() || isAnalyzing}
                                className="w-full bg-red-600 text-white py-4 px-6 rounded-xl hover:bg-red-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-all duration-300 font-semibold text-lg flex items-center justify-center space-x-2"
                            >
                                {isAnalyzing ? (
                                    <>
                                        <Loader2 className="h-5 w-5 animate-spin" />
                                        <span>Analyzing Emergency...</span>
                                    </>
                                ) : (
                                    <>
                                        <AlertTriangle className="h-5 w-5" />
                                        <span>Assess Emergency Level</span>
                                    </>
                                )}
                            </button>
                        </div>
                    </div>
                ) : (
                    /* Results Section */
                    <div className="space-y-6">
                        {/* Alert Header */}
                        <div className={`rounded-2xl p-6 border-2 ${getSeverityColor(alert.severity)}`}>
                            <div className="flex items-center space-x-4 mb-4">
                                {getSeverityIcon(alert.severity)}
                                <div className="flex-1">
                                    <h2 className="text-2xl font-bold capitalize">{alert.severity} Priority</h2>
                                    <p className="text-lg font-semibold">{alert.recommendation}</p>
                                </div>
                                <div className="text-right">
                                    <div className="flex items-center space-x-1 text-sm">
                                        <Clock className="h-4 w-4" />
                                        <span>{alert.timestamp.toLocaleTimeString()}</span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Action Steps */}
                        <div className="bg-white/95 backdrop-blur-sm rounded-2xl shadow-xl border border-gray-200/50 p-6">
                            <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center space-x-2">
                                <Check className="h-6 w-6 text-green-600" />
                                <span>Immediate Actions</span>
                            </h3>
                            <div className="space-y-3">
                                {alert.actions.map((action, index) => (
                                    <div key={index} className="flex items-start space-x-3">
                                        <div className="flex-shrink-0 w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-sm font-bold">
                                            {index + 1}
                                        </div>
                                        <p className="text-gray-800">{action}</p>
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* Emergency Hotlines */}
                        <div className="bg-white/95 backdrop-blur-sm rounded-2xl shadow-xl border border-gray-200/50 p-6">
                            <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center space-x-2">
                                <Phone className="h-6 w-6 text-green-600" />
                                <span>Emergency Contacts</span>
                            </h3>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                {alert.hotlines.map((hotline, index) => (
                                    <div key={index} className="border border-gray-200 rounded-lg p-4">
                                        <div className="flex items-center justify-between mb-2">
                                            <h4 className="font-semibold text-gray-800">{hotline.name}</h4>
                                            <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full">
                                                {hotline.available}
                                            </span>
                                        </div>
                                        <a
                                            href={`tel:${hotline.number}`}
                                            className="flex items-center space-x-2 text-lg font-bold text-blue-600 hover:text-blue-800"
                                        >
                                            <Phone className="h-4 w-4" />
                                            <span>{hotline.number}</span>
                                        </a>
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* Reset Button */}
                        <div className="flex space-x-4">
                            <button
                                onClick={() => {
                                    setAlert(null);
                                    setSymptoms('');
                                }}
                                className="flex-1 bg-gray-600 text-white py-3 px-6 rounded-xl hover:bg-gray-700 transition-colors font-semibold flex items-center justify-center space-x-2"
                            >
                                <X className="h-5 w-5" />
                                <span>New Assessment</span>
                            </button>

                            <Link
                                href="/consultation"
                                className="flex-1 bg-blue-600 text-white py-3 px-6 rounded-xl hover:bg-blue-700 transition-colors font-semibold text-center"
                            >
                                Continue to Consultation
                            </Link>
                        </div>
                    </div>
                )}

                {/* Disclaimer */}
                <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-4 mt-6">
                    <p className="text-sm text-yellow-800">
                        <strong>Disclaimer:</strong> This emergency assessment tool provides general guidance only and should not replace professional medical advice. In case of a genuine emergency, call 999 or 911 immediately or go to the nearest hospital.
                    </p>
                </div>
            </div>
        </div>
    );
}
