'use client';

import React, { useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import { Stethoscope } from 'lucide-react';

interface ProtectedRouteProps {
    children: React.ReactNode;
    requireAuth?: boolean;
}

export default function ProtectedRoute({ children, requireAuth = true }: ProtectedRouteProps) {
    const { isAuthenticated, isLoading } = useAuth();
    const router = useRouter();

    useEffect(() => {
        if (!isLoading && requireAuth && !isAuthenticated) {
            router.push('/login');
        }
    }, [isAuthenticated, isLoading, requireAuth, router]);

    // Show loading state
    if (isLoading) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-100 flex items-center justify-center">
                <div className="text-center">
                    <div className="bg-blue-600 p-6 rounded-3xl inline-block mb-4 shadow-lg animate-pulse">
                        <Stethoscope className="h-16 w-16 text-white" />
                    </div>
                    <p className="text-gray-600">Loading...</p>
                </div>
            </div>
        );
    }

    // Show children if authenticated or auth not required
    if (!requireAuth || isAuthenticated) {
        return <>{children}</>;
    }

    // Return null while redirecting
    return null;
}
