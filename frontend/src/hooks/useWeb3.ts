/**
 * Custom React Hook for Web3/MetaMask Integration
 * Provides wallet connection state and functions
 */

import { useState, useEffect, useCallback } from 'react';
import { web3Service, WalletInfo } from '../services/web3Service';
import { toast } from 'react-hot-toast';

interface UseWeb3Return {
    // State
    isConnected: boolean;
    isConnecting: boolean;
    walletInfo: WalletInfo | null;
    error: string | null;

    // Functions
    connect: () => Promise<void>;
    disconnect: () => Promise<void>;
    switchNetwork: (chainId: string) => Promise<boolean>;
    sendTransaction: (to: string, value: string) => Promise<string | null>;
    signMessage: (message: string) => Promise<string | null>;
    refreshBalance: () => Promise<void>;
}

export function useWeb3(): UseWeb3Return {
    const [isConnected, setIsConnected] = useState(false);
    const [isConnecting, setIsConnecting] = useState(false);
    const [walletInfo, setWalletInfo] = useState<WalletInfo | null>(null);
    const [error, setError] = useState<string | null>(null);

    // Check if already connected on mount
    useEffect(() => {
        checkConnection();
        setupEventListeners();

        return () => {
            web3Service.removeEventListeners();
        };
    }, []);

    const checkConnection = useCallback(async () => {
        try {
            const connected = await web3Service.isConnected();
            if (connected) {
                const account = await web3Service.getCurrentAccount();
                if (account) {
                    const balance = await web3Service.getBalance(account);
                    const chainId = await window.ethereum?.request({ method: 'eth_chainId' });

                    setWalletInfo({
                        address: account,
                        balance,
                        chainId: chainId || '0x1',
                        network: getNetworkName(chainId || '0x1')
                    });
                    setIsConnected(true);
                }
            }
        } catch (err: any) {
            console.error('Error checking connection:', err);
            setError(err.message);
        }
    }, []);

    const getNetworkName = (chainId: string): string => {
        const networks: { [key: string]: string } = {
            '0x1': 'Ethereum Mainnet',
            '0x89': 'Polygon Mainnet',
            '0x38': 'BSC Mainnet',
            '0xaa36a7': 'Sepolia Testnet',
            '0x5': 'Goerli Testnet',
            '0x13881': 'Polygon Mumbai',
            '0x61': 'BSC Testnet'
        };
        return networks[chainId] || `Unknown Network (${chainId})`;
    };

    const setupEventListeners = useCallback(() => {
        if (!web3Service.isMetaMaskInstalled()) return;

        // Handle account changes
        const handleAccountsChanged = (accounts: string[]) => {
            if (accounts.length === 0) {
                // User disconnected
                setIsConnected(false);
                setWalletInfo(null);
                toast.success('Wallet disconnected');
            } else {
                // User switched accounts
                checkConnection();
                toast.success('Account switched');
            }
        };

        // Handle network changes
        const handleChainChanged = (chainId: string) => {
            // Reload the page when network changes (recommended by MetaMask)
            window.location.reload();
        };

        // Handle connection
        const handleConnect = (connectInfo: { chainId: string }) => {
            console.log('MetaMask connected:', connectInfo);
            checkConnection();
        };

        // Handle disconnection
        const handleDisconnect = (error: { code: number; message: string }) => {
            console.log('MetaMask disconnected:', error);
            setIsConnected(false);
            setWalletInfo(null);
            toast.error('Wallet disconnected');
        };

        web3Service.setupEventListeners(
            handleAccountsChanged,
            handleChainChanged,
            handleConnect,
            handleDisconnect
        );
    }, [checkConnection]);

    const connect = useCallback(async () => {
        if (!web3Service.isMetaMaskInstalled()) {
            setError('MetaMask is not installed');
            return;
        }

        setIsConnecting(true);
        setError(null);

        try {
            const wallet = await web3Service.connectWallet();
            if (wallet) {
                setWalletInfo(wallet);
                setIsConnected(true);
            }
        } catch (err: any) {
            setError(err.message);
            toast.error(`Connection failed: ${err.message}`);
        } finally {
            setIsConnecting(false);
        }
    }, []);

    const disconnect = useCallback(async () => {
        try {
            await web3Service.disconnectWallet();
            setIsConnected(false);
            setWalletInfo(null);
            setError(null);
        } catch (err: any) {
            setError(err.message);
        }
    }, []);

    const switchNetwork = useCallback(async (chainId: string): Promise<boolean> => {
        try {
            const success = await web3Service.switchNetwork(chainId);
            if (success) {
                // Update wallet info with new network
                await checkConnection();
            }
            return success;
        } catch (err: any) {
            setError(err.message);
            return false;
        }
    }, [checkConnection]);

    const sendTransaction = useCallback(async (to: string, value: string): Promise<string | null> => {
        if (!walletInfo) {
            toast.error('Wallet not connected');
            return null;
        }

        try {
            const txHash = await web3Service.sendTransaction({
                to,
                value: `0x${(parseFloat(value) * Math.pow(10, 18)).toString(16)}`, // Convert to wei
            });

            if (txHash) {
                // Refresh balance after transaction
                await refreshBalance();
            }

            return txHash;
        } catch (err: any) {
            setError(err.message);
            return null;
        }
    }, [walletInfo]);

    const signMessage = useCallback(async (message: string): Promise<string | null> => {
        if (!walletInfo) {
            toast.error('Wallet not connected');
            return null;
        }

        try {
            return await web3Service.signMessage(message, walletInfo.address);
        } catch (err: any) {
            setError(err.message);
            return null;
        }
    }, [walletInfo]);

    const refreshBalance = useCallback(async () => {
        if (!walletInfo) return;

        try {
            const balance = await web3Service.getBalance(walletInfo.address);
            setWalletInfo(prev => prev ? { ...prev, balance } : null);
        } catch (err: any) {
            console.error('Error refreshing balance:', err);
        }
    }, [walletInfo]);

    return {
        isConnected,
        isConnecting,
        walletInfo,
        error,
        connect,
        disconnect,
        switchNetwork,
        sendTransaction,
        signMessage,
        refreshBalance
    };
}

export default useWeb3;
