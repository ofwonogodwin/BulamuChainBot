'use client';

import React, { useState } from 'react';
import {
    BookOpen,
    Heart,
    Baby,
    Shield,
    Droplets,
    Eye,
    ArrowLeft,
    Play,
    Clock,
    Users,
    Star,
    Search
} from 'lucide-react';
import Link from 'next/link';

interface EducationTopic {
    id: string;
    title: string;
    description: string;
    category: 'prevention' | 'maternal' | 'infectious' | 'chronic' | 'mental' | 'nutrition';
    icon: React.ReactNode;
    readTime: string;
    popularity: number;
    content: {
        overview: string;
        symptoms: string[];
        prevention: string[];
        treatment: string;
        whenToSeek: string;
    };
    localName?: {
        luganda?: string;
        swahili?: string;
    };
}

export default function EducationPage() {
    const [selectedCategory, setSelectedCategory] = useState<string>('all');
    const [selectedTopic, setSelectedTopic] = useState<EducationTopic | null>(null);
    const [searchTerm, setSearchTerm] = useState('');
    const [language, setLanguage] = useState('en');

    const categories = [
        { id: 'all', name: 'All Topics', icon: <BookOpen className="h-4 w-4" /> },
        { id: 'prevention', name: 'Prevention', icon: <Shield className="h-4 w-4" /> },
        { id: 'maternal', name: 'Maternal Health', icon: <Baby className="h-4 w-4" /> },
        { id: 'infectious', name: 'Infectious Diseases', icon: <Droplets className="h-4 w-4" /> },
        { id: 'chronic', name: 'Chronic Conditions', icon: <Heart className="h-4 w-4" /> },
        { id: 'nutrition', name: 'Nutrition', icon: <Users className="h-4 w-4" /> }
    ];

    const topics: EducationTopic[] = [
        {
            id: '1',
            title: 'Malaria Prevention and Treatment',
            description: 'Complete guide to preventing and treating malaria in Uganda',
            category: 'infectious',
            icon: <Droplets className="h-6 w-6" />,
            readTime: '5 min',
            popularity: 95,
            localName: {
                luganda: 'Omusujja gw\'ensiri',
                swahili: 'Malaria'
            },
            content: {
                overview: 'Malaria is one of the leading causes of illness and death in Uganda. It\'s transmitted through bites from infected female Anopheles mosquitoes. Understanding prevention and early treatment is crucial for saving lives.',
                symptoms: [
                    'High fever (usually above 38°C)',
                    'Chills and sweating',
                    'Headache',
                    'Body aches and fatigue',
                    'Nausea and vomiting',
                    'In severe cases: confusion, difficulty breathing'
                ],
                prevention: [
                    'Sleep under insecticide-treated bed nets (ITNs)',
                    'Use mosquito repellent on exposed skin',
                    'Eliminate stagnant water around homes',
                    'Wear long-sleeved clothes during evening/night',
                    'Consider indoor residual spraying',
                    'Take prophylactic medication if traveling to high-risk areas'
                ],
                treatment: 'Seek immediate medical attention for malaria symptoms. Treatment typically involves artemisinin-based combination therapies (ACTs) prescribed by healthcare providers. Complete the full course of medication even if symptoms improve.',
                whenToSeek: 'Seek immediate medical attention if you experience fever, especially if accompanied by chills, headache, or body aches. Severe malaria can be fatal if untreated.'
            }
        },
        {
            id: '2',
            title: 'Maternal Health During Pregnancy',
            description: 'Essential care for expectant mothers and newborns',
            category: 'maternal',
            icon: <Baby className="h-6 w-6" />,
            readTime: '8 min',
            popularity: 88,
            localName: {
                luganda: 'Obulamu bw\'abakazi abali mu lubuto',
                swahili: 'Afya ya mama mjamzito'
            },
            content: {
                overview: 'Proper maternal health care is essential for the health of both mother and baby. Regular prenatal care, proper nutrition, and skilled birth attendance can prevent complications.',
                symptoms: [
                    'Morning sickness (nausea/vomiting)',
                    'Breast tenderness',
                    'Fatigue',
                    'Frequent urination',
                    'Food cravings or aversions'
                ],
                prevention: [
                    'Attend all prenatal care appointments',
                    'Take folic acid supplements',
                    'Eat a balanced diet rich in iron and calcium',
                    'Avoid alcohol, tobacco, and drugs',
                    'Get adequate rest and exercise',
                    'Maintain good hygiene',
                    'Get vaccinated as recommended'
                ],
                treatment: 'Regular prenatal check-ups, proper nutrition, iron and folate supplements, treatment of any complications by qualified healthcare providers.',
                whenToSeek: 'Seek immediate care for severe vomiting, bleeding, severe headaches, blurred vision, severe abdominal pain, or decreased fetal movement.'
            }
        },
        {
            id: '3',
            title: 'Hygiene and Sanitation',
            description: 'Basic hygiene practices to prevent diseases',
            category: 'prevention',
            icon: <Shield className="h-6 w-6" />,
            readTime: '4 min',
            popularity: 82,
            localName: {
                luganda: 'Obuyonjo n\'obulongoofu',
                swahili: 'Usafi na mazingira'
            },
            content: {
                overview: 'Good hygiene and sanitation practices are the foundation of disease prevention. Simple practices can prevent many infectious diseases.',
                symptoms: [
                    'Frequent infections',
                    'Diarrhea',
                    'Skin conditions',
                    'Respiratory infections'
                ],
                prevention: [
                    'Wash hands frequently with soap and clean water',
                    'Use clean, safe drinking water',
                    'Properly dispose of waste',
                    'Keep food covered and cook thoroughly',
                    'Maintain clean living environments',
                    'Practice good personal hygiene',
                    'Use clean toilets/latrines'
                ],
                treatment: 'Focus on prevention through consistent hygiene practices. Treat specific infections as they occur with appropriate medical care.',
                whenToSeek: 'Seek medical care for persistent infections, severe diarrhea, or any concerning symptoms.'
            }
        },
        {
            id: '4',
            title: 'Diabetes Management',
            description: 'Living with and managing diabetes effectively',
            category: 'chronic',
            icon: <Heart className="h-6 w-6" />,
            readTime: '10 min',
            popularity: 76,
            localName: {
                luganda: 'Endwadde y\'esukkali',
                swahili: 'Kisukari'
            },
            content: {
                overview: 'Diabetes is a chronic condition that affects how your body processes blood sugar. With proper management, people with diabetes can live healthy, normal lives.',
                symptoms: [
                    'Frequent urination',
                    'Excessive thirst',
                    'Unexplained weight loss',
                    'Blurred vision',
                    'Slow-healing wounds',
                    'Fatigue'
                ],
                prevention: [
                    'Maintain a healthy weight',
                    'Exercise regularly',
                    'Eat a balanced diet',
                    'Limit sugar and refined carbohydrates',
                    'Don\'t smoke',
                    'Regular health screenings'
                ],
                treatment: 'Regular blood sugar monitoring, medication as prescribed, healthy diet, regular exercise, foot care, regular medical check-ups.',
                whenToSeek: 'Seek immediate care for very high or low blood sugar levels, ketoacidosis symptoms, or serious complications.'
            }
        },
        {
            id: '5',
            title: 'Nutrition for Children',
            description: 'Ensuring proper nutrition for child development',
            category: 'nutrition',
            icon: <Users className="h-6 w-6" />,
            readTime: '6 min',
            popularity: 90,
            localName: {
                luganda: 'Endya ennungi eri abaana',
                swahili: 'Lishe bora kwa watoto'
            },
            content: {
                overview: 'Proper nutrition is crucial for child growth and development. Malnutrition can have lasting effects on physical and cognitive development.',
                symptoms: [
                    'Stunted growth',
                    'Underweight',
                    'Frequent infections',
                    'Delayed development',
                    'Poor concentration'
                ],
                prevention: [
                    'Exclusive breastfeeding for first 6 months',
                    'Introduce diverse foods after 6 months',
                    'Ensure adequate protein intake',
                    'Provide vitamin-rich fruits and vegetables',
                    'Maintain proper food hygiene',
                    'Regular growth monitoring'
                ],
                treatment: 'Nutritional rehabilitation, treatment of underlying conditions, supplementation as needed, nutrition education for caregivers.',
                whenToSeek: 'Seek help for signs of malnutrition, failure to gain weight, or persistent feeding problems.'
            }
        },
        {
            id: '6',
            title: 'HIV/AIDS Awareness and Prevention',
            description: 'Understanding HIV transmission and prevention',
            category: 'infectious',
            icon: <Shield className="h-6 w-6" />,
            readTime: '12 min',
            popularity: 85,
            localName: {
                luganda: 'Okwegendereza HIV/AIDS',
                swahili: 'Kujikinga na HIV/AIDS'
            },
            content: {
                overview: 'HIV is a virus that attacks the immune system. While there\'s no cure, with proper treatment, people with HIV can live long, healthy lives.',
                symptoms: [
                    'Flu-like symptoms (early infection)',
                    'Persistent fatigue',
                    'Unexplained weight loss',
                    'Frequent infections',
                    'Skin rashes',
                    'Swollen lymph nodes'
                ],
                prevention: [
                    'Practice safe sex using condoms',
                    'Get tested regularly',
                    'Avoid sharing needles',
                    'Consider PrEP if high-risk',
                    'Ensure safe blood transfusions',
                    'Prevention of mother-to-child transmission'
                ],
                treatment: 'Antiretroviral therapy (ART), regular medical monitoring, adherence to medication, healthy lifestyle, prevention of opportunistic infections.',
                whenToSeek: 'Seek testing after potential exposure, for regular screening, or if experiencing concerning symptoms.'
            }
        }
    ];

    const filteredTopics = topics.filter(topic => {
        const matchesCategory = selectedCategory === 'all' || topic.category === selectedCategory;
        const matchesSearch = topic.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
            topic.description.toLowerCase().includes(searchTerm.toLowerCase());
        return matchesCategory && matchesSearch;
    });

    const getCategoryColor = (category: string) => {
        switch (category) {
            case 'prevention': return 'bg-green-100 text-green-800';
            case 'maternal': return 'bg-pink-100 text-pink-800';
            case 'infectious': return 'bg-red-100 text-red-800';
            case 'chronic': return 'bg-blue-100 text-blue-800';
            case 'mental': return 'bg-purple-100 text-purple-800';
            case 'nutrition': return 'bg-orange-100 text-orange-800';
            default: return 'bg-gray-100 text-gray-800';
        }
    };

    const getTopicTitle = (topic: EducationTopic) => {
        if (language === 'lg' && topic.localName?.luganda) {
            return topic.localName.luganda;
        }
        if (language === 'sw' && topic.localName?.swahili) {
            return topic.localName.swahili;
        }
        return topic.title;
    };

    if (selectedTopic) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
                {/* Header */}
                <header className="bg-white/90 backdrop-blur-sm border-b border-gray-200/50 p-4">
                    <div className="max-w-4xl mx-auto flex items-center justify-between">
                        <button
                            onClick={() => setSelectedTopic(null)}
                            className="flex items-center space-x-2 text-gray-600 hover:text-gray-800 transition-colors"
                        >
                            <ArrowLeft className="h-5 w-5" />
                            <span className="font-medium">Back to Topics</span>
                        </button>

                        <div className="flex items-center space-x-4">
                            <select
                                value={language}
                                onChange={(e) => setLanguage(e.target.value)}
                                className="bg-white border border-gray-300 rounded-lg px-3 py-1 text-sm"
                            >
                                <option value="en">🇺🇸 English</option>
                                <option value="lg">🇺🇬 Luganda</option>
                                <option value="sw">🇰🇪 Swahili</option>
                            </select>
                        </div>
                    </div>
                </header>

                {/* Topic Content */}
                <div className="max-w-4xl mx-auto p-6">
                    <div className="bg-white/95 backdrop-blur-sm rounded-2xl shadow-xl border border-gray-200/50 p-8">
                        <div className="flex items-center space-x-4 mb-6">
                            <div className="p-3 bg-blue-100 rounded-full">
                                {selectedTopic.icon}
                            </div>
                            <div className="flex-1">
                                <h1 className="text-3xl font-bold text-gray-800">{getTopicTitle(selectedTopic)}</h1>
                                <div className="flex items-center space-x-4 mt-2">
                                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${getCategoryColor(selectedTopic.category)}`}>
                                        {selectedTopic.category.charAt(0).toUpperCase() + selectedTopic.category.slice(1)}
                                    </span>
                                    <div className="flex items-center space-x-1 text-sm text-gray-500">
                                        <Clock className="h-4 w-4" />
                                        <span>{selectedTopic.readTime} read</span>
                                    </div>
                                    <div className="flex items-center space-x-1 text-sm text-gray-500">
                                        <Star className="h-4 w-4" />
                                        <span>{selectedTopic.popularity}% helpful</span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div className="space-y-8">
                            {/* Overview */}
                            <section>
                                <h2 className="text-xl font-bold text-gray-800 mb-3">Overview</h2>
                                <p className="text-gray-700 leading-relaxed">{selectedTopic.content.overview}</p>
                            </section>

                            {/* Symptoms */}
                            <section>
                                <h2 className="text-xl font-bold text-gray-800 mb-3">Signs and Symptoms</h2>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                                    {selectedTopic.content.symptoms.map((symptom, index) => (
                                        <div key={index} className="flex items-center space-x-2 p-3 bg-red-50 rounded-lg">
                                            <div className="w-2 h-2 bg-red-500 rounded-full"></div>
                                            <span className="text-gray-700">{symptom}</span>
                                        </div>
                                    ))}
                                </div>
                            </section>

                            {/* Prevention */}
                            <section>
                                <h2 className="text-xl font-bold text-gray-800 mb-3">Prevention</h2>
                                <div className="space-y-3">
                                    {selectedTopic.content.prevention.map((item, index) => (
                                        <div key={index} className="flex items-start space-x-3 p-3 bg-green-50 rounded-lg">
                                            <div className="flex-shrink-0 w-6 h-6 bg-green-500 text-white rounded-full flex items-center justify-center text-sm font-bold">
                                                {index + 1}
                                            </div>
                                            <span className="text-gray-700">{item}</span>
                                        </div>
                                    ))}
                                </div>
                            </section>

                            {/* Treatment */}
                            <section>
                                <h2 className="text-xl font-bold text-gray-800 mb-3">Treatment</h2>
                                <div className="p-4 bg-blue-50 rounded-lg border-l-4 border-blue-500">
                                    <p className="text-gray-700 leading-relaxed">{selectedTopic.content.treatment}</p>
                                </div>
                            </section>

                            {/* When to Seek Help */}
                            <section>
                                <h2 className="text-xl font-bold text-gray-800 mb-3">When to Seek Medical Help</h2>
                                <div className="p-4 bg-orange-50 rounded-lg border-l-4 border-orange-500">
                                    <p className="text-gray-700 leading-relaxed">{selectedTopic.content.whenToSeek}</p>
                                </div>
                            </section>

                            {/* Actions */}
                            <div className="flex space-x-4 pt-6 border-t border-gray-200">
                                <Link
                                    href="/consultation"
                                    className="flex-1 bg-blue-600 text-white py-3 px-6 rounded-xl hover:bg-blue-700 transition-colors font-semibold text-center"
                                >
                                    Start Consultation
                                </Link>
                                <Link
                                    href="/emergency"
                                    className="flex-1 bg-red-600 text-white py-3 px-6 rounded-xl hover:bg-red-700 transition-colors font-semibold text-center"
                                >
                                    Emergency Help
                                </Link>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
            {/* Header */}
            <header className="bg-white/90 backdrop-blur-sm border-b border-gray-200/50 p-4">
                <div className="max-w-6xl mx-auto flex items-center justify-between">
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
                        <BookOpen className="h-6 w-6 text-blue-600" />
                        <span className="font-semibold text-blue-600">Health Education</span>
                    </div>
                </div>
            </header>

            <div className="max-w-6xl mx-auto p-6">
                {/* Hero Section */}
                <div className="text-center mb-8">
                    <BookOpen className="h-16 w-16 text-blue-500 mx-auto mb-4" />
                    <h1 className="text-4xl font-bold text-gray-800 mb-4">Health Education Center</h1>
                    <p className="text-xl text-gray-600 max-w-2xl mx-auto">
                        Learn about common health conditions, prevention strategies, and when to seek medical care
                    </p>
                </div>

                {/* Search and Filters */}
                <div className="bg-white/95 backdrop-blur-sm rounded-2xl shadow-xl border border-gray-200/50 p-6 mb-8">
                    <div className="flex flex-col md:flex-row space-y-4 md:space-y-0 md:space-x-4">
                        {/* Search */}
                        <div className="flex-1 relative">
                            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                            <input
                                type="text"
                                placeholder="Search health topics..."
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black"
                            />
                        </div>

                        {/* Language Selector */}
                        <select
                            value={language}
                            onChange={(e) => setLanguage(e.target.value)}
                            className="px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 text-black"
                        >
                            <option value="en">English</option>
                            <option value="lg">Luganda</option>
                            <option value="sw">Swahili</option>
                        </select>
                    </div>

                    {/* Category Filters */}
                    <div className="flex flex-wrap gap-3 mt-6">
                        {categories.map((category) => (
                            <button
                                key={category.id}
                                onClick={() => setSelectedCategory(category.id)}
                                className={`flex items-center space-x-2 px-4 py-2 rounded-xl transition-colors ${selectedCategory === category.id
                                        ? 'bg-blue-600 text-white'
                                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                                    }`}
                            >
                                {category.icon}
                                <span className="font-medium">{category.name}</span>
                            </button>
                        ))}
                    </div>
                </div>

                {/* Topics Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {filteredTopics.map((topic) => (
                        <div
                            key={topic.id}
                            onClick={() => setSelectedTopic(topic)}
                            className="bg-white/95 backdrop-blur-sm rounded-2xl shadow-xl border border-gray-200/50 p-6 hover:shadow-2xl transition-all duration-300 cursor-pointer group"
                        >
                            <div className="flex items-center space-x-3 mb-4">
                                <div className="p-2 bg-blue-100 rounded-lg group-hover:bg-blue-200 transition-colors">
                                    {topic.icon}
                                </div>
                                <span className={`px-3 py-1 rounded-full text-sm font-medium ${getCategoryColor(topic.category)}`}>
                                    {topic.category.charAt(0).toUpperCase() + topic.category.slice(1)}
                                </span>
                            </div>

                            <h3 className="text-xl font-bold text-gray-800 mb-2 group-hover:text-blue-600 transition-colors">
                                {getTopicTitle(topic)}
                            </h3>

                            <p className="text-gray-600 mb-4 line-clamp-3">
                                {topic.description}
                            </p>

                            <div className="flex items-center justify-between">
                                <div className="flex items-center space-x-4 text-sm text-gray-500">
                                    <div className="flex items-center space-x-1">
                                        <Clock className="h-4 w-4" />
                                        <span>{topic.readTime}</span>
                                    </div>
                                    <div className="flex items-center space-x-1">
                                        <Star className="h-4 w-4" />
                                        <span>{topic.popularity}%</span>
                                    </div>
                                </div>

                                <Play className="h-5 w-5 text-blue-600 group-hover:text-blue-700 transition-colors" />
                            </div>
                        </div>
                    ))}
                </div>

                {filteredTopics.length === 0 && (
                    <div className="text-center py-12">
                        <BookOpen className="h-16 w-16 text-gray-300 mx-auto mb-4" />
                        <h3 className="text-xl font-semibold text-gray-600 mb-2">No topics found</h3>
                        <p className="text-gray-500">Try adjusting your search or filter criteria</p>
                    </div>
                )}
            </div>
        </div>
    );
}
