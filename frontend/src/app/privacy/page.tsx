'use client';

import React from 'react';
import Link from 'next/link';
import { Stethoscope } from 'lucide-react';

export default function PrivacyPage() {
    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-100 py-12 px-4">
            <div className="max-w-4xl mx-auto">
                {/* Header */}
                <div className="text-center mb-8">
                    <Link href="/" className="inline-flex items-center text-blue-600 hover:text-blue-800 transition-colors mb-6">
                        ← Back to Home
                    </Link>
                    <div className="bg-blue-600 p-4 rounded-2xl inline-block mb-4 shadow-lg">
                        <Stethoscope className="h-12 w-12 text-white" />
                    </div>
                    <h1 className="text-3xl font-bold text-gray-900 mb-2">Privacy Policy</h1>
                    <p className="text-gray-600">Last updated: September 24, 2025</p>
                </div>

                {/* Content */}
                <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-8 space-y-6">
                    <section>
                        <h2 className="text-xl font-semibold text-gray-900 mb-3">1. Information We Collect</h2>
                        <p className="text-gray-600 mb-2">We collect the following types of information:</p>
                        <ul className="text-gray-600 space-y-1 ml-6">
                            <li>• Personal information (name, email, phone number)</li>
                            <li>• Health information and symptoms you provide</li>
                            <li>• Usage data and interaction logs</li>
                            <li>• Device information and IP addresses</li>
                        </ul>
                    </section>

                    <section>
                        <h2 className="text-xl font-semibold text-gray-900 mb-3">2. How We Use Your Information</h2>
                        <p className="text-gray-600 mb-2">Your information is used to:</p>
                        <ul className="text-gray-600 space-y-1 ml-6">
                            <li>• Provide AI-powered health consultations</li>
                            <li>• Maintain and improve our services</li>
                            <li>• Ensure security and prevent fraud</li>
                            <li>• Communicate important updates</li>
                        </ul>
                    </section>

                    <section>
                        <h2 className="text-xl font-semibold text-gray-900 mb-3">3. Data Security</h2>
                        <p className="text-gray-600">
                            We implement industry-standard security measures to protect your data:
                        </p>
                        <ul className="text-gray-600 space-y-1 ml-6 mt-2">
                            <li>• End-to-end encryption for all communications</li>
                            <li>• Blockchain technology for medical records</li>
                            <li>• Regular security audits and updates</li>
                            <li>• Access controls and authentication</li>
                        </ul>
                    </section>

                    <section>
                        <h2 className="text-xl font-semibold text-gray-900 mb-3">4. Data Sharing</h2>
                        <p className="text-gray-600">
                            We do not sell, rent, or share your personal information with third parties except:
                        </p>
                        <ul className="text-gray-600 space-y-1 ml-6 mt-2">
                            <li>• With your explicit consent</li>
                            <li>• When required by law</li>
                            <li>• To healthcare providers you authorize</li>
                            <li>• For emergency medical situations</li>
                        </ul>
                    </section>

                    <section>
                        <h2 className="text-xl font-semibold text-gray-900 mb-3">5. Your Rights</h2>
                        <p className="text-gray-600 mb-2">You have the right to:</p>
                        <ul className="text-gray-600 space-y-1 ml-6">
                            <li>• Access your personal data</li>
                            <li>• Correct inaccurate information</li>
                            <li>• Delete your account and data</li>
                            <li>• Export your medical records</li>
                            <li>• Withdraw consent at any time</li>
                        </ul>
                    </section>

                    <section>
                        <h2 className="text-xl font-semibold text-gray-900 mb-3">6. Medical Data Protection</h2>
                        <p className="text-gray-600">
                            All medical information is treated with the highest level of confidentiality and is subject to additional protections under healthcare privacy regulations. Your medical data is encrypted and stored on a secure blockchain network to ensure immutability and access control.
                        </p>
                    </section>

                    <section>
                        <h2 className="text-xl font-semibold text-gray-900 mb-3">7. Cookies and Tracking</h2>
                        <p className="text-gray-600">
                            We use essential cookies for authentication and functionality. We do not use tracking cookies or share data with advertising networks.
                        </p>
                    </section>

                    <section>
                        <h2 className="text-xl font-semibold text-gray-900 mb-3">8. Children's Privacy</h2>
                        <p className="text-gray-600">
                            Our service is not intended for children under 13. We do not knowingly collect personal information from children under 13 without parental consent.
                        </p>
                    </section>

                    <section>
                        <h2 className="text-xl font-semibold text-gray-900 mb-3">9. Changes to Privacy Policy</h2>
                        <p className="text-gray-600">
                            We may update this privacy policy from time to time. We will notify users of any material changes via email or through our service.
                        </p>
                    </section>

                    <section>
                        <h2 className="text-xl font-semibold text-gray-900 mb-3">10. Contact Us</h2>
                        <p className="text-gray-600">
                            If you have questions about this privacy policy or your data, please contact our privacy team through our support channels.
                        </p>
                    </section>
                </div>
            </div>
        </div>
    );
}
