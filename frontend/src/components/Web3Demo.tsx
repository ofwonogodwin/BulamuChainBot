/**
 * Web3 Demo Component
 * Demonstrates MetaMask integration and blockchain interactions
 */

'use client';

import React, { useState } from 'react';
import { useWeb3 } from '../hooks/useWeb3';
import WalletComponent from './WalletComponent';
import { toast } from 'react-hot-toast';

const Web3Demo: React.FC = () => {
    const {
        isConnected,
        walletInfo,
        sendTransaction,
        signMessage,
        switchNetwork
    } = useWeb3();

    const [recipient, setRecipient] = useState('');
    const [amount, setAmount] = useState('');
    const [message, setMessage] = useState('Hello from BulamuChain!');
    const [signature, setSignature] = useState('');
    const [txHash, setTxHash] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const handleSendTransaction = async () => {
        if (!recipient || !amount) {
            toast.error('Please fill in recipient and amount');
            return;
        }

        if (parseFloat(amount) <= 0) {
            toast.error('Amount must be greater than 0');
            return;
        }

        setIsLoading(true);
        try {
            const hash = await sendTransaction(recipient, amount);
            if (hash) {
                setTxHash(hash);
                setRecipient('');
                setAmount('');
            }
        } catch (error) {
            console.error('Transaction error:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const handleSignMessage = async () => {
        if (!message) {
            toast.error('Please enter a message to sign');
            return;
        }

        setIsLoading(true);
        try {
            const sig = await signMessage(message);
            if (sig) {
                setSignature(sig);
            }
        } catch (error) {
            console.error('Signing error:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const handleSwitchToSepolia = async () => {
        await switchNetwork('0xaa36a7'); // Sepolia testnet
    };

    const handleSwitchToMainnet = async () => {
        await switchNetwork('0x1'); // Ethereum mainnet
    };

    return (
        <div className="max-w-4xl mx-auto p-6 space-y-8">
            {/* Header */}
            <div className="text-center">
                <h1 className="text-3xl font-bold text-gray-900 mb-2">
                    Web3 MetaMask Integration
                </h1>
                <p className="text-gray-600">
                    Connect your MetaMask wallet and interact with the blockchain
                </p>
            </div>

            {/* Wallet Connection */}
            <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-xl font-semibold mb-4">Wallet Connection</h2>
                <WalletComponent
                    showBalance={true}
                    showNetwork={true}
                    className="inline-block"
                />

                {isConnected && walletInfo && (
                    <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div className="bg-blue-50 p-4 rounded-lg">
                            <h3 className="font-semibold text-blue-800 mb-2">Address</h3>
                            <p className="text-sm text-blue-600 break-all">
                                {walletInfo.address}
                            </p>
                        </div>
                        <div className="bg-green-50 p-4 rounded-lg">
                            <h3 className="font-semibold text-green-800 mb-2">Balance</h3>
                            <p className="text-lg font-bold text-green-600">
                                {walletInfo.balance} ETH
                            </p>
                        </div>
                        <div className="bg-purple-50 p-4 rounded-lg">
                            <h3 className="font-semibold text-purple-800 mb-2">Network</h3>
                            <p className="text-sm text-purple-600">
                                {walletInfo.network}
                            </p>
                        </div>
                    </div>
                )}
            </div>

            {isConnected && (
                <>
                    {/* Network Switching */}
                    <div className="bg-white rounded-lg shadow-md p-6">
                        <h2 className="text-xl font-semibold mb-4">Network Operations</h2>
                        <div className="flex flex-wrap gap-4">
                            <button
                                onClick={handleSwitchToMainnet}
                                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors"
                            >
                                Switch to Ethereum Mainnet
                            </button>
                            <button
                                onClick={handleSwitchToSepolia}
                                className="bg-orange-600 hover:bg-orange-700 text-white px-4 py-2 rounded-lg transition-colors"
                            >
                                Switch to Sepolia Testnet
                            </button>
                        </div>
                    </div>

                    {/* Send Transaction */}
                    <div className="bg-white rounded-lg shadow-md p-6">
                        <h2 className="text-xl font-semibold mb-4">Send Transaction</h2>
                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Recipient Address
                                </label>
                                <input
                                    type="text"
                                    value={recipient}
                                    onChange={(e) => setRecipient(e.target.value)}
                                    placeholder="0x..."
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Amount (ETH)
                                </label>
                                <input
                                    type="number"
                                    value={amount}
                                    onChange={(e) => setAmount(e.target.value)}
                                    placeholder="0.001"
                                    step="0.001"
                                    min="0"
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
                                />
                            </div>
                            <button
                                onClick={handleSendTransaction}
                                disabled={isLoading || !recipient || !amount}
                                className="w-full bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-lg font-medium transition-colors"
                            >
                                {isLoading ? 'Sending...' : 'Send Transaction'}
                            </button>
                            {txHash && (
                                <div className="mt-4 p-4 bg-green-50 rounded-lg">
                                    <h4 className="font-semibold text-green-800 mb-2">
                                        Transaction Sent!
                                    </h4>
                                    <p className="text-sm text-green-600 break-all">
                                        Hash: {txHash}
                                    </p>
                                    <a
                                        href={`https://etherscan.io/tx/${txHash}`}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="inline-block mt-2 text-blue-600 hover:text-blue-800 underline"
                                    >
                                        View on Etherscan
                                    </a>
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Message Signing */}
                    <div className="bg-white rounded-lg shadow-md p-6">
                        <h2 className="text-xl font-semibold mb-4">Sign Message</h2>
                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Message to Sign
                                </label>
                                <textarea
                                    value={message}
                                    onChange={(e) => setMessage(e.target.value)}
                                    placeholder="Enter your message here..."
                                    rows={3}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
                                />
                            </div>
                            <button
                                onClick={handleSignMessage}
                                disabled={isLoading || !message}
                                className="w-full bg-purple-600 hover:bg-purple-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-lg font-medium transition-colors"
                            >
                                {isLoading ? 'Signing...' : 'Sign Message'}
                            </button>
                            {signature && (
                                <div className="mt-4 p-4 bg-purple-50 rounded-lg">
                                    <h4 className="font-semibold text-purple-800 mb-2">
                                        Message Signed!
                                    </h4>
                                    <p className="text-sm text-purple-600 break-all">
                                        Signature: {signature}
                                    </p>
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Web3 Tips */}
                    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
                        <h2 className="text-xl font-semibold text-yellow-800 mb-4">
                            💡 Web3 Tips
                        </h2>
                        <ul className="space-y-2 text-yellow-700">
                            <li>• Always double-check recipient addresses before sending transactions</li>
                            <li>• Start with small amounts when testing on mainnet</li>
                            <li>• Use testnets (like Sepolia) for development and testing</li>
                            <li>• Keep your MetaMask extension updated</li>
                            <li>• Never share your private keys or seed phrase</li>
                        </ul>
                    </div>
                </>
            )}

            {!isConnected && (
                <div className="text-center bg-gray-50 rounded-lg p-8">
                    <h3 className="text-lg font-semibold text-gray-700 mb-2">
                        Connect Your Wallet
                    </h3>
                    <p className="text-gray-600 mb-4">
                        Please connect your MetaMask wallet to interact with Web3 features
                    </p>
                    <div className="text-sm text-gray-500">
                        <p>Make sure you have MetaMask installed:</p>
                        <a
                            href="https://metamask.io/download/"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-blue-600 hover:text-blue-800 underline"
                        >
                            Download MetaMask
                        </a>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Web3Demo;
