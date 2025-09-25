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

export default function Navigation() {
    const [isMenuOpen, setIsMenuOpen] = useState(false);
    const [isLanguageOpen, setIsLanguageOpen] = useState(false);

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
        }
    ];

    const languages = [
        { code: 'en', name: 'English', flag: '🇺🇸' },
        { code: 'lg', name: 'Luganda', flag: '🇺🇬' },
        { code: 'sw', name: 'Swahili', flag: '🇰🇪' }
    ];

    return (
        <>
            {/* Mobile Menu Button */}
            <button
                onClick={() => setIsMenuOpen(true)}
                className="fixed top-4 left-4 z-40 md:hidden bg-white/90 backdrop-blur-sm p-2 rounded-xl shadow-lg border border-gray-200/50 hover:bg-white transition-all duration-200"
            >
                <Menu className="h-5 w-5 text-gray-700" />
            </button>

            {/* Language Selector - Top Left for Desktop */}
            <div className="fixed top-6 left-6 z-30 hidden md:block">
                <div className="relative">
                    <button
                        onClick={() => setIsLanguageOpen(!isLanguageOpen)}
                        className="flex items-center space-x-2 bg-white/90 backdrop-blur-sm px-3 py-2 rounded-xl shadow-lg border border-gray-200/50 hover:bg-white transition-all duration-200"
                    >
                        <Globe className="h-4 w-4 text-blue-600" />
                        <span className="text-sm font-medium text-gray-700">English</span>
                        <ChevronDown className="h-3 w-3 text-gray-500" />
                    </button>

                    {isLanguageOpen && (
                        <div className="absolute top-full mt-2 left-0 bg-white rounded-xl shadow-xl border border-gray-200/50 py-2 min-w-[120px] z-50">
                            {languages.map((lang) => (
                                <button
                                    key={lang.code}
                                    className="w-full flex items-center space-x-3 px-4 py-2 text-sm hover:bg-gray-50 transition-colors"
                                    onClick={() => {
                                        // Handle language change here
                                        setIsLanguageOpen(false);
                                    }}
                                >
                                    <span>{lang.flag}</span>
                                    <span>{lang.name}</span>
                                </button>
                            ))}
                        </div>
                    )}
                </div>
            </div>

            {/* Feature Navigation - Bottom */}
            <div className="fixed bottom-6 left-1/2 transform -translate-x-1/2 z-30 hidden md:block">
                <div className="bg-white/95 backdrop-blur-sm rounded-2xl shadow-xl border border-gray-200/50 p-4">
                    <div className="flex items-center space-x-6">
                        {features.map((feature, index) => (
                            <Link
                                key={index}
                                href={feature.href}
                                className="relative group flex flex-col items-center space-y-2 p-3 rounded-xl hover:bg-gray-50 transition-all duration-200"
                            >
                                <div className="flex items-center justify-center w-10 h-10 bg-blue-50 rounded-full group-hover:bg-blue-100 transition-colors">
                                    {feature.icon}
                                </div>
                                <span className="text-xs font-medium text-gray-600 group-hover:text-gray-800">
                                    {feature.title}
                                </span>
                                {feature.badge && (
                                    <div className={`absolute -top-1 -right-1 px-1.5 py-0.5 rounded-full text-[10px] font-bold ${feature.badge === 'Critical'
                                            ? 'bg-red-500 text-white'
                                            : 'bg-green-500 text-white'
                                        }`}>
                                        {feature.badge}
                                    </div>
                                )}

                                {/* Tooltip */}
                                <div className="absolute bottom-full mb-2 left-1/2 transform -translate-x-1/2 hidden group-hover:block">
                                    <div className="bg-gray-800 text-white text-xs px-2 py-1 rounded whitespace-nowrap">
                                        {feature.description}
                                    </div>
                                </div>
                            </Link>
                        ))}
                    </div>
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
                                >
                                    <X className="h-5 w-5 text-gray-500" />
                                </button>
                            </div>

                            {/* Language Selector */}
                            <div className="mb-6">
                                <h3 className="text-sm font-medium text-gray-500 mb-3">Language</h3>
                                <div className="grid grid-cols-1 gap-2">
                                    {languages.map((lang) => (
                                        <button
                                            key={lang.code}
                                            className="flex items-center space-x-3 p-3 rounded-xl hover:bg-gray-50 transition-colors"
                                        >
                                            <span className="text-lg">{lang.flag}</span>
                                            <span className="font-medium">{lang.name}</span>
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
