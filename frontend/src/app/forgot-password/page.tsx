'use client';

import React, { useState } from 'react';
import { Stethoscope } from 'lucide-react';
import Link from 'next/link';
import { authService } from '@/services/api';

export default function ForgotPasswordPage() {
    const [email, setEmail] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setMessage('');
        setIsLoading(true);

        try {
            const response = await authService.requestPasswordReset(email);

            if (response.success) {
                setMessage('Password reset instructions have been sent to your email address.');
            } else {
                setError(response.message || 'Failed to send reset instructions. Please try again.');
            }
        } catch (error) {
            console.error('Password reset error:', error);
            setError('An error occurred. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-100 flex items-center justify-center px-4">
            <div className="w-full max-w-md">
                {/* Back to login */}
                <div className="text-center mb-8">
                    <Link href="/login" className="inline-flex items-center text-blue-600 hover:text-blue-800 transition-colors">
                        ← Back to Sign In
                    </Link>
                </div>

                {/* Logo and Title */}
                <div className="text-center mb-8">
                    <div className="bg-blue-600 p-4 rounded-2xl inline-block mb-4 shadow-lg">
                        <Stethoscope className="h-12 w-12 text-white" />
                    </div>
                    <h1 className="text-2xl font-semibold text-gray-800 mb-1">Reset Password</h1>
                    <p className="text-gray-500">Enter your email to receive reset instructions</p>
                </div>

                {/* Form */}
                <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6">
                    <form onSubmit={handleSubmit} className="space-y-4">
                        {error && (
                            <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg text-sm">
                                {error}
                            </div>
                        )}

                        {message && (
                            <div className="bg-green-50 border border-green-200 text-green-600 px-4 py-3 rounded-lg text-sm">
                                {message}
                            </div>
                        )}

                        <div>
                            <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                                Email Address
                            </label>
                            <input
                                id="email"
                                type="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                placeholder="Enter your email address"
                                className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                required
                            />
                        </div>

                        <button
                            type="submit"
                            disabled={isLoading}
                            className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors font-medium"
                        >
                            {isLoading ? 'Sending...' : 'Send Reset Instructions'}
                        </button>
                    </form>

                    <div className="mt-6 pt-6 border-t border-gray-200 text-center">
                        <p className="text-gray-600">
                            Remember your password?{' '}
                            <Link href="/login" className="text-blue-600 hover:text-blue-800 font-medium">
                                Sign In
                            </Link>
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}
