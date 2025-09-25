'use client';

import React, { useState, useEffect } from 'react';
import {
    Shield,
    CheckCircle,
    AlertCircle,
    Copy,
    ExternalLink,
    ArrowLeft,
    Hash,
    Calendar,
    User,
    FileText,
    Loader2,
    Eye
} from 'lucide-react';
import Link from 'next/link';

interface BlockchainRecord {
    id: string;
    transactionHash: string;
    blockNumber: number;
    timestamp: Date;
    recordType: 'consultation' | 'prescription' | 'test_result' | 'diagnosis';
    patientId: string;
    providerId?: string;
    ipfsHash: string;
    verified: boolean;
    gasUsed: number;
    gasPrice: string;
}

interface VerificationResult {
    isValid: boolean;
    record?: BlockchainRecord;
    error?: string;
    integrityCheck: boolean;
    timestampValid: boolean;
    signatureValid: boolean;
}

export default function BlockchainPage() {
    const [transactionHash, setTransactionHash] = useState('');
    const [isVerifying, setIsVerifying] = useState(false);
    const [verificationResult, setVerificationResult] = useState<VerificationResult | null>(null);
    const [recentRecords, setRecentRecords] = useState<BlockchainRecord[]>([]);
    const [showDemo, setShowDemo] = useState(false);

    useEffect(() => {
        // Load sample records for demo
        loadSampleRecords();
    }, []);

    const loadSampleRecords = () => {
        const sampleRecords: BlockchainRecord[] = [
            {
                id: '1',
                transactionHash: '0x742d35cc6df32ba4c7d1c5f3e8b3f9ea1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e',
                blockNumber: 18542890,
                timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000), // 2 hours ago
                recordType: 'consultation',
                patientId: 'patient-001',
                providerId: 'dr-smith',
                ipfsHash: 'QmZ4tDuvesekSs4qM5ZBKpXiZGun7S2CYtEZRB3DYXkjGx',
                verified: true,
                gasUsed: 21000,
                gasPrice: '20.5'
            },
            {
                id: '2',
                transactionHash: '0xa1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456',
                blockNumber: 18542785,
                timestamp: new Date(Date.now() - 6 * 60 * 60 * 1000), // 6 hours ago
                recordType: 'prescription',
                patientId: 'patient-002',
                providerId: 'dr-johnson',
                ipfsHash: 'QmYwAPJzv5CZsnAzt1WiQmT2ubMRGEn4GztyXjmGrwbVT2',
                verified: true,
                gasUsed: 25000,
                gasPrice: '22.1'
            },
            {
                id: '3',
                transactionHash: '0x9f8e7d6c5b4a39281726354859607485968574836291058374659281740593',
                blockNumber: 18542650,
                timestamp: new Date(Date.now() - 12 * 60 * 60 * 1000), // 12 hours ago
                recordType: 'test_result',
                patientId: 'patient-003',
                providerId: 'lab-central',
                ipfsHash: 'QmPZ9gcCEpqKTo6aq61g4nDP8xg8co7RK9BDkYCKB6bFqX',
                verified: true,
                gasUsed: 18500,
                gasPrice: '19.8'
            }
        ];
        setRecentRecords(sampleRecords);
    };

    const verifyRecord = async () => {
        if (!transactionHash.trim()) return;

        setIsVerifying(true);
        setVerificationResult(null);

        try {
            // Simulate blockchain verification
            await new Promise(resolve => setTimeout(resolve, 3000));

            // Check if it's one of our sample records
            const sampleRecord = recentRecords.find(r =>
                r.transactionHash.toLowerCase() === transactionHash.toLowerCase()
            );

            if (sampleRecord) {
                const result: VerificationResult = {
                    isValid: true,
                    record: sampleRecord,
                    integrityCheck: true,
                    timestampValid: true,
                    signatureValid: true
                };
                setVerificationResult(result);
            } else {
                // Generate a mock verification result for demo
                const mockRecord: BlockchainRecord = {
                    id: Date.now().toString(),
                    transactionHash: transactionHash,
                    blockNumber: 18543000 + Math.floor(Math.random() * 1000),
                    timestamp: new Date(Date.now() - Math.random() * 24 * 60 * 60 * 1000),
                    recordType: 'consultation',
                    patientId: 'patient-demo',
                    providerId: 'dr-demo',
                    ipfsHash: 'QmDemo' + Math.random().toString(36).substring(2, 15),
                    verified: Math.random() > 0.2, // 80% chance of being verified
                    gasUsed: 20000 + Math.floor(Math.random() * 10000),
                    gasPrice: (18 + Math.random() * 10).toFixed(1)
                };

                const result: VerificationResult = {
                    isValid: mockRecord.verified,
                    record: mockRecord.verified ? mockRecord : undefined,
                    error: mockRecord.verified ? undefined : 'Record not found or verification failed',
                    integrityCheck: mockRecord.verified,
                    timestampValid: mockRecord.verified,
                    signatureValid: mockRecord.verified
                };
                setVerificationResult(result);
            }

        } catch (error) {
            setVerificationResult({
                isValid: false,
                error: 'Network error during verification',
                integrityCheck: false,
                timestampValid: false,
                signatureValid: false
            });
        } finally {
            setIsVerifying(false);
        }
    };

    const copyToClipboard = (text: string) => {
        navigator.clipboard.writeText(text);
        // You could add a toast notification here
    };

    const getRecordTypeColor = (type: string) => {
        switch (type) {
            case 'consultation': return 'bg-blue-100 text-blue-800';
            case 'prescription': return 'bg-green-100 text-green-800';
            case 'test_result': return 'bg-purple-100 text-purple-800';
            case 'diagnosis': return 'bg-orange-100 text-orange-800';
            default: return 'bg-gray-100 text-gray-800';
        }
    };

    const formatRecordType = (type: string) => {
        return type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-green-50 via-white to-blue-50">
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
                        <Shield className="h-6 w-6 text-green-600" />
                        <span className="font-semibold text-green-600">Blockchain Verification</span>
                    </div>
                </div>
            </header>

            <div className="max-w-6xl mx-auto p-4">
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Verification Input */}
                    <div className="lg:col-span-2">
                        <div className="bg-white/95 backdrop-blur-sm rounded-2xl shadow-xl border border-gray-200/50 p-8">
                            <div className="text-center mb-8">
                                <Shield className="h-16 w-16 text-green-500 mx-auto mb-4" />
                                <h1 className="text-3xl font-bold text-gray-800 mb-2">Verify Medical Record</h1>
                                <p className="text-gray-600">
                                    Enter transaction hash to verify authenticity and integrity
                                </p>
                            </div>

                            <div className="space-y-6">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                        Transaction Hash:
                                    </label>
                                    <div className="relative">
                                        <input
                                            type="text"
                                            value={transactionHash}
                                            onChange={(e) => setTransactionHash(e.target.value)}
                                            placeholder="0x742d35cc6df32ba4c7d1c5f3e8b3f9ea1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e"
                                            className="w-full p-4 pr-12 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent font-mono text-sm text-black"
                                        />
                                        <Hash className="absolute right-4 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                                    </div>
                                </div>

                                <div className="flex space-x-4">
                                    <button
                                        onClick={verifyRecord}
                                        disabled={!transactionHash.trim() || isVerifying}
                                        className="flex-1 bg-green-600 text-white py-4 px-6 rounded-xl hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-all duration-300 font-semibold flex items-center justify-center space-x-2"
                                    >
                                        {isVerifying ? (
                                            <>
                                                <Loader2 className="h-5 w-5 animate-spin" />
                                                <span>Verifying...</span>
                                            </>
                                        ) : (
                                            <>
                                                <Shield className="h-5 w-5" />
                                                <span>Verify Record</span>
                                            </>
                                        )}
                                    </button>

                                    <button
                                        onClick={() => setShowDemo(!showDemo)}
                                        className="px-6 py-4 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-colors font-semibold"
                                    >
                                        <Eye className="h-5 w-5" />
                                    </button>
                                </div>

                                {showDemo && (
                                    <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
                                        <h4 className="font-semibold text-blue-800 mb-2">Try Demo Hashes:</h4>
                                        <div className="space-y-2 text-sm">
                                            {recentRecords.slice(0, 2).map((record, index) => (
                                                <button
                                                    key={index}
                                                    onClick={() => setTransactionHash(record.transactionHash)}
                                                    className="block w-full text-left font-mono text-blue-700 hover:text-blue-900 truncate"
                                                >
                                                    {record.transactionHash}
                                                </button>
                                            ))}
                                        </div>
                                    </div>
                                )}
                            </div>
                        </div>

                        {/* Verification Results */}
                        {verificationResult && (
                            <div className="mt-6 bg-white/95 backdrop-blur-sm rounded-2xl shadow-xl border border-gray-200/50 p-8">
                                <div className="flex items-center space-x-4 mb-6">
                                    {verificationResult.isValid ? (
                                        <CheckCircle className="h-10 w-10 text-green-600" />
                                    ) : (
                                        <AlertCircle className="h-10 w-10 text-red-600" />
                                    )}
                                    <div>
                                        <h3 className="text-2xl font-bold text-gray-800">
                                            {verificationResult.isValid ? 'Verification Successful' : 'Verification Failed'}
                                        </h3>
                                        <p className={`text-lg ${verificationResult.isValid ? 'text-green-600' : 'text-red-600'}`}>
                                            {verificationResult.isValid
                                                ? 'Record is authentic and verified'
                                                : verificationResult.error || 'Record verification failed'
                                            }
                                        </p>
                                    </div>
                                </div>

                                {verificationResult.record && (
                                    <div className="space-y-6">
                                        {/* Verification Checks */}
                                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                            <div className="flex items-center space-x-3 p-4 bg-gray-50 rounded-lg">
                                                <CheckCircle className={`h-6 w-6 ${verificationResult.integrityCheck ? 'text-green-600' : 'text-red-600'}`} />
                                                <div>
                                                    <p className="font-semibold">Data Integrity</p>
                                                    <p className="text-sm text-gray-600">
                                                        {verificationResult.integrityCheck ? 'Verified' : 'Failed'}
                                                    </p>
                                                </div>
                                            </div>

                                            <div className="flex items-center space-x-3 p-4 bg-gray-50 rounded-lg">
                                                <CheckCircle className={`h-6 w-6 ${verificationResult.timestampValid ? 'text-green-600' : 'text-red-600'}`} />
                                                <div>
                                                    <p className="font-semibold">Timestamp</p>
                                                    <p className="text-sm text-gray-600">
                                                        {verificationResult.timestampValid ? 'Valid' : 'Invalid'}
                                                    </p>
                                                </div>
                                            </div>

                                            <div className="flex items-center space-x-3 p-4 bg-gray-50 rounded-lg">
                                                <CheckCircle className={`h-6 w-6 ${verificationResult.signatureValid ? 'text-green-600' : 'text-red-600'}`} />
                                                <div>
                                                    <p className="font-semibold">Signature</p>
                                                    <p className="text-sm text-gray-600">
                                                        {verificationResult.signatureValid ? 'Valid' : 'Invalid'}
                                                    </p>
                                                </div>
                                            </div>
                                        </div>

                                        {/* Record Details */}
                                        <div className="border-t border-gray-200 pt-6">
                                            <h4 className="text-lg font-semibold text-gray-800 mb-4">Record Details</h4>
                                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                                <div className="space-y-3">
                                                    <div>
                                                        <label className="text-sm font-medium text-gray-500">Record Type</label>
                                                        <div className="mt-1">
                                                            <span className={`inline-flex px-3 py-1 rounded-full text-sm font-medium ${getRecordTypeColor(verificationResult.record.recordType)}`}>
                                                                {formatRecordType(verificationResult.record.recordType)}
                                                            </span>
                                                        </div>
                                                    </div>

                                                    <div>
                                                        <label className="text-sm font-medium text-gray-500">Block Number</label>
                                                        <p className="text-gray-800 font-mono">{verificationResult.record.blockNumber.toLocaleString()}</p>
                                                    </div>

                                                    <div>
                                                        <label className="text-sm font-medium text-gray-500">Timestamp</label>
                                                        <p className="text-gray-800">{verificationResult.record.timestamp.toLocaleString()}</p>
                                                    </div>
                                                </div>

                                                <div className="space-y-3">
                                                    <div>
                                                        <label className="text-sm font-medium text-gray-500">Transaction Hash</label>
                                                        <div className="flex items-center space-x-2">
                                                            <p className="text-gray-800 font-mono text-sm truncate">{verificationResult.record.transactionHash}</p>
                                                            <button
                                                                onClick={() => copyToClipboard(verificationResult.record!.transactionHash)}
                                                                className="text-gray-400 hover:text-gray-600"
                                                            >
                                                                <Copy className="h-4 w-4" />
                                                            </button>
                                                        </div>
                                                    </div>

                                                    <div>
                                                        <label className="text-sm font-medium text-gray-500">IPFS Hash</label>
                                                        <div className="flex items-center space-x-2">
                                                            <p className="text-gray-800 font-mono text-sm truncate">{verificationResult.record.ipfsHash}</p>
                                                            <button
                                                                onClick={() => copyToClipboard(verificationResult.record!.ipfsHash)}
                                                                className="text-gray-400 hover:text-gray-600"
                                                            >
                                                                <Copy className="h-4 w-4" />
                                                            </button>
                                                        </div>
                                                    </div>

                                                    <div>
                                                        <label className="text-sm font-medium text-gray-500">Gas Used</label>
                                                        <p className="text-gray-800">{verificationResult.record.gasUsed.toLocaleString()} Gwei</p>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>

                                        {/* Actions */}
                                        <div className="border-t border-gray-200 pt-6">
                                            <div className="flex space-x-4">
                                                <button className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                                                    <ExternalLink className="h-4 w-4" />
                                                    <span>View on Explorer</span>
                                                </button>

                                                <button className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors">
                                                    <FileText className="h-4 w-4" />
                                                    <span>Download Certificate</span>
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                )}
                            </div>
                        )}
                    </div>

                    {/* Recent Records Sidebar */}
                    <div className="lg:col-span-1">
                        <div className="bg-white/95 backdrop-blur-sm rounded-2xl shadow-xl border border-gray-200/50 p-6">
                            <h3 className="text-xl font-bold text-gray-800 mb-4">Recent Records</h3>

                            <div className="space-y-4">
                                {recentRecords.map((record) => (
                                    <div key={record.id} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors">
                                        <div className="flex items-center justify-between mb-2">
                                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${getRecordTypeColor(record.recordType)}`}>
                                                {formatRecordType(record.recordType)}
                                            </span>
                                            {record.verified && (
                                                <CheckCircle className="h-4 w-4 text-green-600" />
                                            )}
                                        </div>

                                        <p className="font-mono text-xs text-gray-600 truncate mb-2">
                                            {record.transactionHash}
                                        </p>

                                        <div className="flex items-center space-x-2 text-xs text-gray-500">
                                            <Calendar className="h-3 w-3" />
                                            <span>{record.timestamp.toLocaleDateString()}</span>
                                        </div>

                                        <button
                                            onClick={() => setTransactionHash(record.transactionHash)}
                                            className="w-full mt-2 text-xs bg-blue-100 text-blue-600 py-1 rounded hover:bg-blue-200 transition-colors"
                                        >
                                            Verify This Record
                                        </button>
                                    </div>
                                ))}
                            </div>

                            <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg">
                                <div className="flex items-center space-x-2 mb-2">
                                    <Shield className="h-5 w-5 text-green-600" />
                                    <span className="font-semibold text-green-800">Blockchain Security</span>
                                </div>
                                <p className="text-sm text-green-700">
                                    All medical records are cryptographically secured and tamper-proof on the blockchain.
                                </p>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Info Section */}
                <div className="mt-8 bg-white/95 backdrop-blur-sm rounded-2xl shadow-xl border border-gray-200/50 p-6">
                    <h3 className="text-xl font-bold text-gray-800 mb-4">How Blockchain Verification Works</h3>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        <div className="text-center">
                            <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
                                <Hash className="h-6 w-6 text-blue-600" />
                            </div>
                            <h4 className="font-semibold mb-2">Immutable Records</h4>
                            <p className="text-sm text-gray-600">
                                Medical records are hashed and stored on blockchain, making them tamper-proof.
                            </p>
                        </div>

                        <div className="text-center">
                            <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3">
                                <Shield className="h-6 w-6 text-green-600" />
                            </div>
                            <h4 className="font-semibold mb-2">Cryptographic Security</h4>
                            <p className="text-sm text-gray-600">
                                Digital signatures ensure authenticity and non-repudiation of medical data.
                            </p>
                        </div>

                        <div className="text-center">
                            <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-3">
                                <CheckCircle className="h-6 w-6 text-purple-600" />
                            </div>
                            <h4 className="font-semibold mb-2">Instant Verification</h4>
                            <p className="text-sm text-gray-600">
                                Anyone can verify the authenticity of records using transaction hashes.
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
