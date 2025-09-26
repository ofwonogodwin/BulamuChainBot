'use client';

import React, { createContext, useContext, useState, ReactNode } from 'react';

// Language configuration
export const LANGUAGES = [
  { code: 'en', name: 'English', voice: 'en-US' },
  { code: 'lg', name: 'Luganda', voice: 'en-US' },
  { code: 'sw', name: 'Swahili', voice: 'sw-KE' }
];

// Emergency page translations
export const EMERGENCY_TRANSLATIONS = {
  en: {
    pageTitle: "Emergency Health Assessment",
    subtitle: "Describe your symptoms for immediate risk assessment and guidance",
    currentLocation: "Current Location",
    locationHelp: "💡 Location helps emergency services find you faster. Please enable in your browser settings.",
    retryLocation: "Retry Location",
    symptomsLabel: "Describe your symptoms in detail:",
    symptomsPlaceholder: "e.g., severe chest pain, difficulty breathing, fever of 39°C...",
    assessEmergency: "Assess Emergency Level",
    analyzing: "Analyzing Emergency...",
    emergencyHotlines: "Emergency Hotlines",
    analysisResults: "Emergency Analysis Results",
    severityLevel: "Severity Level",
    recommendation: "Recommendation",
    immediateActions: "Immediate Actions",
    relevantHotlines: "Relevant Emergency Contacts",
    callEmergency: "Call Emergency Services",
    criticalAlert: "CRITICAL - SEEK IMMEDIATE HELP",
    highAlert: "HIGH - Urgent Medical Attention",
    mediumAlert: "MEDIUM - Medical Consultation Needed",
    lowAlert: "LOW - Monitor and Rest",
    gettingLocation: "Getting location...",
    locationUnavailable: "Location unavailable",
    locationDenied: "Location access denied. Please enable location in browser settings.",
    locationTimeout: "Location request timed out",
    locationError: "Location error",
    geolocationNotSupported: "Geolocation not supported by this browser"
  },
  lg: {
    pageTitle: "Okukebera Obulwadde bw'Amaangu",
    subtitle: "Nnyonyola obubonero bwo oweebwe obuyambi bw'amaangu n'okukulagirwa",
    currentLocation: "Ekifo ky'Oli",
    locationHelp: "💡 Okumanya gy'oli kuyamba abasawo b'amaangu okukuzuula amangu. Nsaba okkirize mu browser yo.",
    retryLocation: "Ddamu Okugezaako",
    symptomsLabel: "Nnyonyola obubonero bwo mu bunnyonnyozi:",
    symptomsPlaceholder: "gamba ng'obulumi bw'ekifuba obw'amaangu, okukaluubirwa okussa omukka, omusujja gw'emyaka 39...",
    assessEmergency: "Kebera Omutindo gw'Obulwadde bw'Amaangu",
    analyzing: "Nkekebera Obulwadde bw'Amaangu...",
    emergencyHotlines: "Ennamba z'Amaangu",
    analysisResults: "Ebivudde mu Kukebera kw'Amaangu",
    severityLevel: "Omutindo gw'Obukulu",
    recommendation: "Ekiragiddwa",
    immediateActions: "Ebikolwa by'Amaangu",
    relevantHotlines: "Ennamba z'Amaangu ez'Enkulu",
    callEmergency: "Kuba Abasawo b'Amaangu",
    criticalAlert: "KYA MAANGU NNYO - NOONYA OBUYAMBI AMANGU",
    highAlert: "KYA MAANGU - Obujjanjabi bw'Amaangu Bwetaagisa",
    mediumAlert: "KYA WAKATI - Obujjanjabi Bwetaagisa",
    lowAlert: "SI KYA MAANGU - Weekuume era Wewummule",
    gettingLocation: "Nfuna ekifo ky'oli...",
    locationUnavailable: "Ekifo tekifunibwa",
    locationDenied: "Tewakkirizza kufuna ekifo. Nsaba okkirize mu browser yo.",
    locationTimeout: "Okusaba ekifo kumaze ebiseera.",
    locationError: "Kiremye okufuna ekifo",
    geolocationNotSupported: "Browser eno teyinza kufuna bifo"
  },
  sw: {
    pageTitle: "Tathmini ya Dharura ya Afya",
    subtitle: "Elezea dalili zako kwa tathmini ya haraka ya hatari na mwongozo",
    currentLocation: "Mahali Ulipo Sasa",
    locationHelp: "💡 Kutambua mahali ulipo kunasaidia huduma za dharura kukupata haraka. Tafadhali ruhusu katika mipangilio ya kivinjari chako.",
    retryLocation: "Jaribu Tena Mahali",
    symptomsLabel: "Elezea dalili zako kwa undani:",
    symptomsPlaceholder: "k.m., maumivu makali ya kifua, ugumu wa kupumua, homa ya nyuzi 39...",
    assessEmergency: "Tathmini Kiwango cha Dharura",
    analyzing: "Nachanganua Dharura...",
    emergencyHotlines: "Nambari za Dharura",
    analysisResults: "Matokeo ya Uchambuzi wa Dharura",
    severityLevel: "Kiwango cha Ukali",
    recommendation: "Mapendekezo",
    immediateActions: "Hatua za Haraka",
    relevantHotlines: "Mawasiliano Muhimu ya Dharura",
    callEmergency: "Piga Huduma za Dharura",
    criticalAlert: "HATARI - TAFUTA MSAADA WA HARAKA",
    highAlert: "JUKUMU LA JUU - Matibabu ya Haraka Yanahitajika",
    mediumAlert: "WASTANI - Ushauri wa Kimatibabu Unahitajika",
    lowAlert: "CHINI - Fuatilia na Pumzika",
    gettingLocation: "Napata mahali ulipo...",
    locationUnavailable: "Mahali haupatikani",
    locationDenied: "Ufikiaji wa mahali umekataliwa. Tafadhali ruhusu katika mipangilio ya kivinjari.",
    locationTimeout: "Ombi la mahali limechelewa.",
    locationError: "Hitilafu ya mahali",
    geolocationNotSupported: "Kivinjari hiki hakitumii huduma ya mahali"
  }
};

// Language context interface
interface LanguageContextType {
  currentLanguage: string;
  setCurrentLanguage: (language: string) => void;
  getCurrentLanguageData: () => typeof LANGUAGES[0];
  getPlaceholderText: () => string;
  getGreetingText: () => string;
  getEmergencyTranslations: () => typeof EMERGENCY_TRANSLATIONS.en;
}

// Create context
const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

// Provider component
export const LanguageProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [currentLanguage, setCurrentLanguage] = useState('en');

  const getCurrentLanguageData = () => {
    return LANGUAGES.find(lang => lang.code === currentLanguage) || LANGUAGES[0];
  };

  const getPlaceholderText = () => {
    switch (currentLanguage) {
      case 'lg':
        return 'Nnyonyola obubonero bwo oba ebikuluma...';
      case 'sw':
        return 'Elezea dalili zako au maswali yako ya afya...';
      default:
        return 'Tell me about your symptoms or health concerns...';
    }
  };

  const getGreetingText = () => {
    switch (currentLanguage) {
      case 'lg':
        return 'Tusanyukireko kukulaba! Tunasobola kutuyambe tutya?';
      case 'sw':
        return 'Karibu! Tunaweza kusaidiaje?';
      default:
        return 'Welcome! How can we help you today?';
    }
  };

  const getEmergencyTranslations = () => {
    return EMERGENCY_TRANSLATIONS[currentLanguage as keyof typeof EMERGENCY_TRANSLATIONS] || EMERGENCY_TRANSLATIONS.en;
  };

  const value: LanguageContextType = {
    currentLanguage,
    setCurrentLanguage,
    getCurrentLanguageData,
    getPlaceholderText,
    getGreetingText,
    getEmergencyTranslations,
  };

  return (
    <LanguageContext.Provider value={value}>
      {children}
    </LanguageContext.Provider>
  );
};

// Hook to use language context
export const useLanguage = (): LanguageContextType => {
  const context = useContext(LanguageContext);
  if (context === undefined) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
};