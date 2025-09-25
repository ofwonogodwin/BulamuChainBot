'use client';

import React, { createContext, useContext, useState, ReactNode } from 'react';

// Language configuration
export const LANGUAGES = [
  { code: 'en', name: 'English', voice: 'en-US' },
  { code: 'lg', name: 'Luganda', voice: 'en-US' },
  { code: 'sw', name: 'Swahili', voice: 'sw-KE' }
];

// Language context interface
interface LanguageContextType {
  currentLanguage: string;
  setCurrentLanguage: (language: string) => void;
  getCurrentLanguageData: () => typeof LANGUAGES[0];
  getPlaceholderText: () => string;
  getGreetingText: () => string;
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

  const value: LanguageContextType = {
    currentLanguage,
    setCurrentLanguage,
    getCurrentLanguageData,
    getPlaceholderText,
    getGreetingText,
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