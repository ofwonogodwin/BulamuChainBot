'use client';

import React from 'react';
import { Stethoscope, MessageCircle, Shield, QrCode, Users, Heart } from 'lucide-react';
import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';

export default function HomePage() {
  const { isAuthenticated, user } = useAuth();

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-100">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-sm shadow-sm border-b border-blue-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-3">
              <div className="bg-blue-600 p-2 rounded-xl">
                <Stethoscope className="h-8 w-8 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-blue-900">BulamuChainBot</h1>
                <p className="text-sm text-blue-600">AI Health Assistant</p>
              </div>
            </div>

            <nav className="flex items-center space-x-4">
              {isAuthenticated ? (
                <div className="flex items-center space-x-4">
                  <span className="text-blue-700">Welcome, {user?.first_name}!</span>
                  <Link
                    href="/dashboard"
                    className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    Dashboard
                  </Link>
                </div>
              ) : (
                <div className="flex items-center space-x-3">
                  <Link
                    href="/login"
                    className="text-blue-600 hover:text-blue-800 transition-colors"
                  >
                    Sign In
                  </Link>
                  <Link
                    href="/register"
                    className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    Get Started
                  </Link>
                </div>
              )}
            </nav>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl sm:text-6xl font-bold text-blue-900 mb-6">
            Your AI-Powered
            <span className="block text-blue-600">Health Assistant</span>
          </h2>
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            BulamuChainBot brings advanced healthcare to rural Uganda with AI consultations,
            blockchain-verified medical records, and multilingual support in English and Luganda.
          </p>

          {!isAuthenticated && (
            <div className="flex flex-col sm:flex-row justify-center gap-4 mb-12">
              <Link
                href="/register"
                className="bg-blue-600 text-white px-8 py-4 rounded-xl text-lg font-semibold hover:bg-blue-700 transform hover:scale-105 transition-all duration-200 shadow-lg"
              >
                Start Free Consultation
              </Link>
              <Link
                href="/about"
                className="bg-white text-blue-600 px-8 py-4 rounded-xl text-lg font-semibold border-2 border-blue-600 hover:bg-blue-50 transition-colors"
              >
                Learn More
              </Link>
            </div>
          )}

          {/* Demo Chat Interface Preview */}
          <div className="bg-white rounded-2xl shadow-xl border border-blue-100 p-6 max-w-2xl mx-auto">
            <div className="flex items-center space-x-3 mb-4 pb-4 border-b border-gray-100">
              <div className="bg-blue-100 p-2 rounded-full">
                <MessageCircle className="h-5 w-5 text-blue-600" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">AI Health Assistant</h3>
                <p className="text-sm text-gray-500">Available 24/7 in English & Luganda</p>
              </div>
            </div>

            <div className="space-y-4 text-left">
              <div className="bg-gray-100 p-3 rounded-lg rounded-bl-sm">
                <p className="text-gray-800">Hello! I am your AI health assistant. How are you feeling today?</p>
              </div>
              <div className="bg-blue-600 text-white p-3 rounded-lg rounded-br-sm ml-8">
                <p>I have a headache and fever. Can you help me?</p>
              </div>
              <div className="bg-gray-100 p-3 rounded-lg rounded-bl-sm">
                <p className="text-gray-800">I will help you assess your symptoms. How long have you had these symptoms?</p>
              </div>
            </div>

            <div className="mt-4 pt-4 border-t border-gray-100">
              <div className="flex items-center justify-between text-sm text-gray-500">
                <span className="flex items-center space-x-1">
                  <Shield className="h-4 w-4" />
                  <span>Secure & Private</span>
                </span>
                <span className="flex items-center space-x-1">
                  <QrCode className="h-4 w-4" />
                  <span>Medicine Verification</span>
                </span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h3 className="text-3xl font-bold text-gray-900 mb-4">
              Comprehensive Healthcare Solutions
            </h3>
            <p className="text-xl text-gray-600">
              Bridging the healthcare gap with technology and compassion
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            <FeatureCard
              icon={<MessageCircle className="h-8 w-8" />}
              title="AI Consultations"
              description="24/7 AI-powered health consultations in English and Luganda with emergency detection."
            />
            <FeatureCard
              icon={<Shield className="h-8 w-8" />}
              title="Blockchain Records"
              description="Secure, tamper-proof medical records stored on blockchain with patient consent controls."
            />
            <FeatureCard
              icon={<QrCode className="h-8 w-8" />}
              title="Medicine Verification"
              description="QR code scanning to verify medicine authenticity and prevent counterfeit drugs."
            />
            <FeatureCard
              icon={<Users className="h-8 w-8" />}
              title="Doctor Network"
              description="Connect with verified healthcare providers and specialists when needed."
            />
            <FeatureCard
              icon={<Heart className="h-8 w-8" />}
              title="Health Tracking"
              description="Monitor your health metrics and receive personalized recommendations."
            />
            <FeatureCard
              icon={<Stethoscope className="h-8 w-8" />}
              title="Emergency Alerts"
              description="Automatic emergency detection and alert system for critical health situations."
            />
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-blue-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8">
            <div className="md:col-span-2">
              <div className="flex items-center space-x-3 mb-4">
                <div className="bg-blue-600 p-2 rounded-xl">
                  <Stethoscope className="h-6 w-6 text-white" />
                </div>
                <h4 className="text-xl font-bold">BulamuChainBot</h4>
              </div>
              <p className="text-blue-200 mb-4">
                Democratizing healthcare access in rural Uganda through AI and blockchain technology.
              </p>
              <p className="text-sm text-blue-300">
                Built for the community, powered by innovation.
              </p>
            </div>

            <div>
              <h5 className="font-semibold mb-4">Quick Links</h5>
              <ul className="space-y-2 text-blue-200">
                <li><Link href="/about" className="hover:text-white transition-colors">About Us</Link></li>
                <li><Link href="/privacy" className="hover:text-white transition-colors">Privacy Policy</Link></li>
                <li><Link href="/terms" className="hover:text-white transition-colors">Terms of Service</Link></li>
                <li><Link href="/contact" className="hover:text-white transition-colors">Contact</Link></li>
              </ul>
            </div>

            <div>
              <h5 className="font-semibold mb-4">Support</h5>
              <ul className="space-y-2 text-blue-200">
                <li><Link href="/help" className="hover:text-white transition-colors">Help Center</Link></li>
                <li><Link href="/faq" className="hover:text-white transition-colors">FAQ</Link></li>
                <li><Link href="/emergency" className="hover:text-white transition-colors">Emergency</Link></li>
              </ul>
            </div>
          </div>

          <div className="border-t border-blue-800 mt-8 pt-8 text-center text-blue-300">
            <p>&copy; 2024 BulamuChainBot. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}

interface FeatureCardProps {
  icon: React.ReactNode;
  title: string;
  description: string;
}

function FeatureCard({ icon, title, description }: FeatureCardProps) {
  return (
    <div className="bg-blue-50 p-6 rounded-xl border border-blue-100 hover:shadow-lg transition-shadow">
      <div className="bg-blue-600 text-white p-3 rounded-lg inline-block mb-4">
        {icon}
      </div>
      <h4 className="text-xl font-semibold text-gray-900 mb-3">{title}</h4>
      <p className="text-gray-600">{description}</p>
    </div>
  );
}
