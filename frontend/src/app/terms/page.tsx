'use client';

import React from 'react';
import Link from 'next/link';
import { Stethoscope } from 'lucide-react';

export default function TermsPage() {
    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-100 py-12 px-4">
            <div className="max-w-4xl mx-auto">
                {/* Header */}
                <div className="text-center mb-8">
                    <Link href="/" className="inline-flex items-center text-blue-600 hover:text-blue-800 transition-colors mb-6">
                        Back
                    </Link>
                    <div className="bg-blue-600 p-4 rounded-2xl inline-block mb-4 shadow-lg">
                        <Stethoscope className="h-12 w-12 text-white" />
                    </div>
                    <h1 className="text-3xl font-bold text-gray-900 mb-2">Terms of Service</h1>
                    <p className="text-gray-600">Last updated: September 24, 2025</p>
                </div>

                {/* Content */}
                <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-8 space-y-6">
                    <section>
                        <h2 className="text-xl font-semibold text-gray-900 mb-3">1. Acceptance of Terms</h2>
                        <p className="text-gray-600">
                            By accessing and using BulamuChainBot, you accept and agree to be bound by the terms and provision of this agreement.
                        </p>
                    </section>

                    <section>
                        <h2 className="text-xl font-semibold text-gray-900 mb-3">2. Medical Disclaimer</h2>
                        <p className="text-gray-600">
                            BulamuChainBot provides AI-assisted health information and consultation services. This service is not a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of your physician or other qualified health provider with any questions you may have regarding a medical condition.
                        </p>
                    </section>

                    <section>
                        <h2 className="text-xl font-semibold text-gray-900 mb-3">3. User Responsibilities</h2>
                        <p className="text-gray-600 mb-2">You agree to:</p>
                        <ul className="text-gray-600 space-y-1 ml-6">
                            <li>• Provide accurate and truthful information</li>
                            <li>• Use the service responsibly and lawfully</li>
                            <li>• Respect the privacy and rights of other users</li>
                            <li>• Not misuse the AI consultation feature</li>
                        </ul>
                    </section>

                    <section>
                        <h2 className="text-xl font-semibold text-gray-900 mb-3">4. Privacy and Data Protection</h2>
                        <p className="text-gray-600">
                            Your privacy is important to us. All medical data is encrypted and stored securely on blockchain technology. We comply with applicable data protection regulations and maintain strict confidentiality standards.
                        </p>
                    </section>

                    <section>
                        <h2 className="text-xl font-semibold text-gray-900 mb-3">5. Emergency Situations</h2>
                        <p className="text-red-600">
                            <strong>Important:</strong> BulamuChainBot is not designed for emergency medical situations. In case of a medical emergency, immediately contact local emergency services or go to the nearest hospital.
                        </p>
                    </section>

                    <section>
                        <h2 className="text-xl font-semibold text-gray-900 mb-3">6. Limitation of Liability</h2>
                        <p className="text-gray-600">
                            BulamuChainBot and its operators shall not be liable for any direct, indirect, incidental, special, or consequential damages resulting from the use or inability to use the service.
                        </p>
                    </section>

                    <section>
                        <h2 className="text-xl font-semibold text-gray-900 mb-3">7. Changes to Terms</h2>
                        <p className="text-gray-600">
                            We reserve the right to modify these terms at any time. Changes will be posted on this page with an updated revision date.
                        </p>
                    </section>

                    <section>
                        <h2 className="text-xl font-semibold text-gray-900 mb-3">8. Contact Information</h2>
                        <p className="text-gray-600">
                            If you have any questions about these Terms of Service, please contact us through our support channels.
                        </p>
                    </section>
                </div>
            </div>
        </div>
    );
}
