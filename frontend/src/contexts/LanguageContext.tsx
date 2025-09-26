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
    geolocationNotSupported: "Geolocation not supported by this browser",
    // Recommendations
    criticalRecommendation: "IMMEDIATE MEDICAL ATTENTION REQUIRED",
    highRecommendation: "Seek urgent medical attention within 1 hour",
    mediumRecommendation: "Medical consultation recommended within 24 hours",
    lowRecommendation: "Monitor symptoms and consider medical consultation",
    // Actions for critical
    criticalAction1: "Call emergency services immediately (999 or 911)",
    criticalAction2: "Do not move unless absolutely necessary",
    criticalAction3: "Stay calm and follow emergency operator instructions",
    criticalAction4: "Have someone stay with you until help arrives",
    criticalAction5: "If possible, have medical history and medications ready",
    // Actions for high
    highAction1: "Contact nearest hospital or clinic immediately",
    highAction2: "Consider calling emergency services if symptoms worsen",
    highAction3: "Monitor symptoms closely",
    highAction4: "Have someone accompany you to medical facility",
    highAction5: "Bring identification and medical information",
    // Actions for medium
    mediumAction1: "Schedule appointment with healthcare provider",
    mediumAction2: "Monitor symptoms and note any changes",
    mediumAction3: "Take basic first aid measures if applicable",
    mediumAction4: "Rest and stay hydrated",
    mediumAction5: "Seek immediate help if symptoms worsen",
    // Actions for low
    lowAction1: "Keep track of symptoms",
    lowAction2: "Try basic home remedies if appropriate",
    lowAction3: "Schedule non-urgent medical appointment if symptoms persist",
    lowAction4: "Rest and maintain good health practices",
    lowAction5: "Contact healthcare provider if concerned",
    // Display labels
    priority: "Priority",
    emergencyContacts: "Emergency Contacts"
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
    geolocationNotSupported: "Browser eno teyinza kufuna bifo",
    // Recommendations
    criticalRecommendation: "OBUJJANJABI BW'AMAANGU BWETAAGISA AMANGU",
    highRecommendation: "Noonya obujjanjabi bw'amaangu mu saawa emu",
    mediumRecommendation: "Obujjanjabi bwetaagisa mu nnaku 24",
    lowRecommendation: "Weekuume era olowoze ku kugenda ku musawo",
    // Actions for critical
    criticalAction1: "Kuba abasawo b'amaangu amangu (999 oba 911)",
    criticalAction2: "Totambula wabula nga kyetaagisa nnyo",
    criticalAction3: "Beera muttekeefu era goberera ebiragiro by'abasawo",
    criticalAction4: "Omuntu abe naawe okutuusa abasawo lwe banaakutuuka",
    criticalAction5: "Bwe kisoboka, beera n'ebyafaayo bye bulwadde ne ddagala",
    // Actions for high
    highAction1: "Kuba eddwaliro oba kiliniki amangu",
    highAction2: "Lowooza okukuba abasawo bwe binaayongera okuba bibi",
    highAction3: "Kuuma ng'olaba obubonero bwo",
    highAction4: "Omuntu akwegatteko okugenda mu ddwaliro",
    highAction5: "Twalaawo endagiriro yo n'amawulire g'obulwadde bwo",
    // Actions for medium
    mediumAction1: "Teekawo olunaku okusisinkana n'omusawo",
    mediumAction2: "Kuuma ng'olaba obubonero bwo era owandike enkyukakyuka",
    mediumAction3: "Kola obuyambi obw'omusingi bwe kisoboka",
    mediumAction4: "Wewummule era onywe amazzi amalungi",
    mediumAction5: "Noonya obuyambi amangu bwe kinaayongera okuba kibi",
    // Actions for low
    lowAction1: "Kuuma ng'ogoberera obubonero bwo",
    lowAction2: "Gezaako obujjanjabi obw'ewaka bwe kisoboka",
    lowAction3: "Teekawo okusisinkana n'omusawo obubonero bwe bunaasigala",
    lowAction4: "Wewummule era okwate empisa nnungi ez'obulamu",
    lowAction5: "Tusanyukira n'omusawo bw'onaabanga ofaayo",
    // Display labels
    priority: "Omutindo",
    emergencyContacts: "Ennamba z'Amaangu"
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
    geolocationNotSupported: "Kivinjari hiki hakitumii huduma ya mahali",
    // Recommendations
    criticalRecommendation: "MATIBABU YA HARAKA YANAHITAJIKA SASA HIVI",
    highRecommendation: "Tafuta matibabu ya haraka ndani ya saa moja",
    mediumRecommendation: "Ushauri wa kimatibabu unapendekeza ndani ya masaa 24",
    lowRecommendation: "Fuatilia dalili na ufikiria kutembelea mtaalamu wa afya",
    // Actions for critical
    criticalAction1: "Piga huduma za dharura mara moja (999 au 911)",
    criticalAction2: "Usihamishwe isipokuwa ni lazimi sana",
    criticalAction3: "Utulivu na fuata maelekezo ya mwendeshaji wa dharura",
    criticalAction4: "Mtu awe nawe hadi msaada utakapofikia",
    criticalAction5: "Ikiwezekana, kuwa na historia ya afya na madawa",
    // Actions for high
    highAction1: "Wasiliana na hospitali au kliniki karibu mara moja",
    highAction2: "Fikiria kupiga huduma za dharura dalili zikizidi kuwa mbaya",
    highAction3: "Fuatilia dalili kwa makini",
    highAction4: "Mtu akuongozee kwenda kituo cha afya",
    highAction5: "Leta kitambulisho na habari za kiafya",
    // Actions for medium
    mediumAction1: "Panga miadi na mtoa huduma za afya",
    mediumAction2: "Fuatilia dalili na andika mabadiliko yoyote",
    mediumAction3: "Tumia njia za kwanza za msaada ikiwezekana",
    mediumAction4: "Pumzika na kunywa maji mengi",
    mediumAction5: "Tafuta msaada wa haraka dalili zikizidi kuwa mbaya",
    // Actions for low
    lowAction1: "Fuatilia dalili zako",
    lowAction2: "Jaribu dawa za nyumbani ikiwezekana",
    lowAction3: "Panga miadi isiyo ya dharura dalili zikiendelea",
    lowAction4: "Pumzika na dumu na mazoea mazuri ya afya",
    lowAction5: "Wasiliana na mtoa huduma za afya ukihisi wasiwasi",
    // Display labels
    priority: "Kipaumbele",
    emergencyContacts: "Mawasiliano ya Dharura"
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