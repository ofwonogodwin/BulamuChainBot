/**
 * Web3 Test Page
 * Test page for MetaMask integration and Web3 functionality
 */

import React from 'react';
import Web3Demo from '../../components/Web3Demo';

export default function Web3TestPage() {
    return (
        <div className="min-h-screen bg-gray-50 py-8">
            <div className="container mx-auto px-4">
                <Web3Demo />
            </div>
        </div>
    );
}
