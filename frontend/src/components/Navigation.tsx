'use client';

import React, { useState } from 'react';
import {
    Mic,
    Globe,
    Shield,
    BookOpen,
    Activity,
    ChevronDown,
    Menu,
    X,
    BarChart3
} from 'lucide-react';
import Link from 'next/link';
import { useLanguage, LANGUAGES } from '@/contexts/LanguageContext';
import WalletComponent from './WalletComponent';

export default function Navigation() {
    const [isMenuOpen, setIsMenuOpen] = useState(false);
    const [isLanguageOpen, setIsLanguageOpen] = useState(false);
    const { currentLanguage, setCurrentLanguage, getCurrentLanguageData } = useLanguage();

    const features = [
        {
            icon: <Mic className="h-4 w-4" />,
            title: 'Voice Chat',
            description: 'Talk to AI in your language',
            href: '/voice-consultation',
            badge: 'New'
        },
        {
            icon: <Activity className="h-4 w-4" />,
            title: 'Emergency',
            description: 'Quick emergency assistance',
            href: '/emergency',
            badge: 'Critical'
        },
        {
            icon: <Shield className="h-4 w-4" />,
            title: 'Blockchain',
            description: 'Verify your medical records',
            href: '/blockchain',
            badge: null
        },
        {
            icon: <BookOpen className="h-4 w-4" />,
            title: 'Education',
            description: 'Learn about health topics',
            href: '/education',
            badge: null
        },
        {
            icon: <BarChart3 className="h-4 w-4" />,
            title: 'Web3 Test',
            description: 'Test MetaMask integration',
            href: '/web3-test',
            badge: 'Demo'
        }
    ];



    return (
        <>
            {/* Mobile Menu Button */}
            <button
                onClick={() => setIsMenuOpen(true)}
                className="fixed top-4 left-4 z-40 md:hidden bg-white/90 backdrop-blur-sm p-2 rounded-xl shadow-lg border border-gray-200/50 hover:bg-white transition-all duration-200"
                title="Open Menu"
            >
                <Menu className="h-5 w-5 text-gray-700" />
            </button>

            {/* Wallet Component - Top Right for Desktop */}
            <div className="fixed top-6 right-48 z-30 hidden md:block">
                <WalletComponent className="inline-block" />
            </div>

            {/* Language Selector - Top Right for Desktop */}
            <div className="fixed top-6 right-24 z-30 hidden md:block">
                <div className="relative">
                    <button
                        onClick={() => setIsLanguageOpen(!isLanguageOpen)}
                        className="flex items-center space-x-2 bg-white/90 backdrop-blur-sm px-3 py-2 rounded-xl shadow-lg border border-gray-200/50 hover:bg-white transition-all duration-200"
                        title="Select Language"
                    >
                        <Globe className="h-4 w-4 text-blue-600" />
                        <span className="text-sm font-medium text-black">
                            {getCurrentLanguageData().name}
                        </span>
                        <ChevronDown className="h-3 w-3 text-gray-500" />
                    </button>

                    {isLanguageOpen && (
                        <div className="absolute top-full mt-2 left-0 bg-white rounded-xl shadow-xl border border-gray-200/50 py-2 min-w-[120px] z-50">
                            {LANGUAGES.map((lang) => (
                                <button
                                    key={lang.code}
                                    className="w-full flex items-center space-x-3 px-4 py-2 text-sm text-black hover:bg-gray-50 transition-colors"
                                    onClick={() => {
                                        setCurrentLanguage(lang.code);
                                        setIsLanguageOpen(false);
                                    }}
                                    title={`Switch to ${lang.name}`}
                                >
                                    <span className="text-black">{lang.name}</span>
                                </button>
                            ))}
                        </div>
                    )}
                </div>
            </div>



            {/* Mobile Slide-out Menu */}
            {isMenuOpen && (
                <div className="fixed inset-0 z-50 md:hidden">
                    {/* Backdrop */}
                    <div
                        className="fixed inset-0 bg-black/50 backdrop-blur-sm"
                        onClick={() => setIsMenuOpen(false)}
                    />

                    {/* Menu Panel */}
                    <div className="fixed left-0 top-0 bottom-0 w-80 bg-white shadow-2xl transform transition-transform duration-300">
                        <div className="p-6">
                            {/* Header */}
                            <div className="flex items-center justify-between mb-8">
                                <div className="flex items-center space-x-3">
                                    <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                                        <Activity className="h-4 w-4 text-white" />
                                    </div>
                                    <span className="font-semibold text-gray-800">BulamuChain</span>
                                </div>
                                <button
                                    onClick={() => setIsMenuOpen(false)}
                                    className="p-2 rounded-lg hover:bg-gray-100"
                                    title="Close Menu"
                                >
                                    <X className="h-5 w-5 text-gray-500" />
                                </button>
                            </div>

                            {/* Language Selector */}
                            <div className="mb-6">
                                <h3 className="text-sm font-medium text-gray-500 mb-3">Language</h3>
                                <div className="space-y-2">
                                    {LANGUAGES.map((lang) => (
                                        <button
                                            key={lang.code}
                                            className={`w-full flex items-center space-x-3 px-3 py-2 text-sm rounded-lg hover:bg-gray-50 transition-colors ${currentLanguage === lang.code ? 'bg-blue-50 text-blue-600' : 'text-black'
                                                }`}
                                            onClick={() => {
                                                setCurrentLanguage(lang.code);
                                                setIsMenuOpen(false);
                                            }}
                                            title={`Switch to ${lang.name}`}
                                        >
                                            <span className={currentLanguage === lang.code ? 'text-blue-600' : 'text-black'}>{lang.name}</span>
                                        </button>
                                    ))}
                                </div>
                            </div>

                            {/* Features */}
                            <div>
                                <h3 className="text-sm font-medium text-gray-500 mb-3">Features</h3>
                                <div className="space-y-2">
                                    {features.map((feature, index) => (
                                        <Link
                                            key={index}
                                            href={feature.href}
                                            className="flex items-center space-x-3 p-4 rounded-xl hover:bg-gray-50 transition-colors group"
                                            onClick={() => setIsMenuOpen(false)}
                                        >
                                            <div className="flex items-center justify-center w-10 h-10 bg-blue-50 rounded-full group-hover:bg-blue-100 transition-colors">
                                                {feature.icon}
                                            </div>
                                            <div className="flex-1">
                                                <div className="flex items-center space-x-2">
                                                    <span className="font-medium text-gray-800">{feature.title}</span>
                                                    {feature.badge && (
                                                        <span className={`px-1.5 py-0.5 rounded-full text-[10px] font-bold ${feature.badge === 'Critical'
                                                            ? 'bg-red-500 text-white'
                                                            : 'bg-green-500 text-white'
                                                            }`}>
                                                            {feature.badge}
                                                        </span>
                                                    )}
                                                </div>
                                                <p className="text-sm text-gray-500">{feature.description}</p>
                                            </div>
                                        </Link>
                                    ))}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </>
    );
}
