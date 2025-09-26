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
    Loader2,
    Globe
} from 'lucide-react';
import Link from 'next/link';
import { useLanguage, LANGUAGES } from '@/contexts/LanguageContext';

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
    const { currentLanguage, setCurrentLanguage, getEmergencyTranslations } = useLanguage();
    const t = getEmergencyTranslations();

    const [symptoms, setSymptoms] = useState('');
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [alert, setAlert] = useState<EmergencyAlert | null>(null);
    const [location, setLocation] = useState(t.gettingLocation); const emergencyHotlines = [
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
                setLocation(t.geolocationNotSupported);
                return;
            }

            navigator.geolocation.getCurrentPosition(
                (position) => {
                    // In a real app, you would reverse geocode this to get the address
                    setLocation(`Lat: ${position.coords.latitude.toFixed(4)}, Long: ${position.coords.longitude.toFixed(4)}`);
                },
                (error) => {
                    let errorMessage = t.locationUnavailable;

                    switch (error.code) {
                        case error.PERMISSION_DENIED:
                            errorMessage = t.locationDenied;
                            break;
                        case error.POSITION_UNAVAILABLE:
                            errorMessage = t.locationUnavailable;
                            break;
                        case error.TIMEOUT:
                            errorMessage = t.locationTimeout;
                            break;
                        default:
                            errorMessage = `${t.locationError}: ${error.message}`;
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
    }, [t]);

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
                recommendation = t.criticalRecommendation;
                actions = [
                    t.criticalAction1,
                    t.criticalAction2,
                    t.criticalAction3,
                    t.criticalAction4,
                    t.criticalAction5
                ];
            } else if (hasHighSeveritySymptoms) {
                severity = 'high';
                recommendation = t.highRecommendation;
                actions = [
                    t.highAction1,
                    t.highAction2,
                    t.highAction3,
                    t.highAction4,
                    t.highAction5
                ];
            } else if (lowerSymptoms.includes('fever') || lowerSymptoms.includes('pain')) {
                severity = 'medium';
                recommendation = t.mediumRecommendation;
                actions = [
                    t.mediumAction1,
                    t.mediumAction2,
                    t.mediumAction3,
                    t.mediumAction4,
                    t.mediumAction5
                ];
            } else {
                severity = 'low';
                recommendation = t.lowRecommendation;
                actions = [
                    t.lowAction1,
                    t.lowAction2,
                    t.lowAction3,
                    t.lowAction4,
                    t.lowAction5
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

                    <div className="flex items-center space-x-4">
                        <div className="flex items-center space-x-2">
                            <AlertTriangle className="h-6 w-6 text-red-600" />
                            <span className="font-semibold text-red-600">Emergency Assistant</span>
                        </div>

                        {/* Language Selector */}
                        <select
                            value={currentLanguage}
                            onChange={(e) => setCurrentLanguage(e.target.value)}
                            className="bg-white border border-gray-300 rounded-lg px-3 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-red-500"
                        >
                            {LANGUAGES.map(lang => (
                                <option key={lang.code} value={lang.code}>
                                    {lang.name}
                                </option>
                            ))}
                        </select>
                    </div>
                </div>
            </header>

            <div className="max-w-4xl mx-auto p-4">
                {!alert ? (
                    /* Input Section */
                    <div className="bg-white/95 backdrop-blur-sm rounded-2xl shadow-xl border border-gray-200/50 p-8 mb-6">
                        <div className="text-center mb-8">
                            <AlertTriangle className="h-16 w-16 text-red-500 mx-auto mb-4" />
                            <h1 className="text-3xl font-bold text-gray-800 mb-2">{t.pageTitle}</h1>
                            <p className="text-gray-600">
                                {t.subtitle}
                            </p>
                        </div>

                        <div className="space-y-6">
                            {/* Location Status */}
                            <div className="bg-gray-50 p-4 rounded-lg border">
                                <div className="flex items-center justify-between mb-2">
                                    <div className="flex items-center space-x-2">
                                        <MapPin className="h-4 w-4 text-red-600" />
                                        <span className="text-sm font-medium text-gray-700">{t.currentLocation}</span>
                                    </div>
                                    {(location.includes('unavailable') || location.includes('denied') || location.includes('error') || location.includes('not supported') || location.includes('timeout') || location === t.locationUnavailable || location === t.locationDenied || location === t.locationTimeout || location === t.geolocationNotSupported) && (
                                        <button
                                            onClick={() => {
                                                if (navigator.geolocation) {
                                                    setLocation(t.gettingLocation);
                                                    navigator.geolocation.getCurrentPosition(
                                                        (position) => {
                                                            setLocation(`Lat: ${position.coords.latitude.toFixed(4)}, Long: ${position.coords.longitude.toFixed(4)}`);
                                                        },
                                                        (error) => {
                                                            let errorMessage = t.locationUnavailable;
                                                            switch (error.code) {
                                                                case error.PERMISSION_DENIED:
                                                                    errorMessage = t.locationDenied;
                                                                    break;
                                                                case error.POSITION_UNAVAILABLE:
                                                                    errorMessage = t.locationUnavailable;
                                                                    break;
                                                                case error.TIMEOUT:
                                                                    errorMessage = t.locationTimeout;
                                                                    break;
                                                                default:
                                                                    errorMessage = `${t.locationError}: ${error.message || 'Unknown error'}`;
                                                                    break;
                                                            }
                                                            setLocation(errorMessage);
                                                        },
                                                        {
                                                            enableHighAccuracy: false,
                                                            timeout: 10000,
                                                            maximumAge: 300000
                                                        }
                                                    );
                                                } else {
                                                    setLocation(t.geolocationNotSupported);
                                                }
                                            }}
                                            className="px-3 py-1 bg-red-600 text-white text-xs rounded hover:bg-red-700 transition-colors"
                                        >
                                            {t.retryLocation}
                                        </button>
                                    )}
                                </div>
                                <p className="text-sm text-gray-600">{location}</p>
                                {(location === t.locationDenied || location === t.geolocationNotSupported) && (
                                    <p className="text-xs text-gray-500 mt-2">
                                        {t.locationHelp}
                                    </p>
                                )}
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    {t.symptomsLabel}
                                </label>
                                <textarea
                                    value={symptoms}
                                    onChange={(e) => setSymptoms(e.target.value)}
                                    placeholder={t.symptomsPlaceholder}
                                    className="w-full h-32 p-4 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent resize-none text-black"
                                    rows={4}
                                />
                            </div>

                            <button
                                onClick={analyzeEmergency}
                                disabled={!symptoms.trim() || isAnalyzing}
                                className="w-full bg-red-600 text-white py-4 px-6 rounded-xl hover:bg-red-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-all duration-300 font-semibold text-lg flex items-center justify-center space-x-2"
                            >
                                {isAnalyzing ? (
                                    <>
                                        <Loader2 className="h-5 w-5 animate-spin" />
                                        <span>{t.analyzing}</span>
                                    </>
                                ) : (
                                    <>
                                        <AlertTriangle className="h-5 w-5" />
                                        <span>{t.assessEmergency}</span>
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
                                    <h2 className="text-2xl font-bold capitalize">{alert.severity} {t.priority}</h2>
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
                                <span>{t.immediateActions}</span>
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
                                <span>{t.emergencyContacts}</span>
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
