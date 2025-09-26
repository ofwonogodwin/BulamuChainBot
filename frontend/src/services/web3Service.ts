/**
 * Web3 Service for MetaMask Integration
 * Handles wallet connection, transaction management, and blockchain interactions
 */

import { toast } from 'react-hot-toast';

// Define types for Web3 integration
declare global {
    interface Window {
        ethereum?: {
            isMetaMask?: boolean;
            request: (args: { method: string; params?: any[] }) => Promise<any>;
            on: (eventName: string, handler: (...args: any[]) => void) => void;
            removeListener: (eventName: string, handler: (...args: any[]) => void) => void;
            selectedAddress?: string;
            chainId?: string;
        };
    }
}

export interface WalletInfo {
    address: string;
    balance: string;
    chainId: string;
    network: string;
}

export interface TransactionRequest {
    to: string;
    value?: string;
    data?: string;
    gas?: string;
    gasPrice?: string;
}

class Web3Service {
    private static instance: Web3Service;
    private isConnecting = false;

    static getInstance(): Web3Service {
        if (!Web3Service.instance) {
            Web3Service.instance = new Web3Service();
        }
        return Web3Service.instance;
    }

    /**
     * Check if MetaMask is installed
     */
    isMetaMaskInstalled(): boolean {
        return typeof window !== 'undefined' &&
            typeof window.ethereum !== 'undefined' &&
            Boolean(window.ethereum.isMetaMask);
    }

    /**
     * Get the current network name from chain ID
     */
    private getNetworkName(chainId: string): string {
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
    }

    /**
     * Connect to MetaMask wallet
     */
    async connectWallet(): Promise<WalletInfo | null> {
        if (!this.isMetaMaskInstalled()) {
            toast.error('MetaMask is not installed. Please install MetaMask extension.');
            window.open('https://metamask.io/download/', '_blank');
            return null;
        }

        if (this.isConnecting) {
            toast.error('Connection already in progress...');
            return null;
        }

        try {
            this.isConnecting = true;

            // Check if wallet was previously disconnected - if so, force fresh connection
            const wasDisconnected = localStorage.getItem('wallet_disconnected');
            if (wasDisconnected) {
                // Clear the disconnect flag first
                localStorage.removeItem('wallet_disconnected');

                // This will force MetaMask to show the connection prompt again
                toast.loading('Requesting wallet connection...');
            }

            // Request account access - this will show MetaMask popup
            const accounts = await window.ethereum!.request({
                method: 'eth_requestAccounts'
            });

            if (!accounts || accounts.length === 0) {
                toast.error('No accounts found. Please check your MetaMask wallet.');
                return null;
            }

            const address = accounts[0];

            // Get balance
            const balance = await this.getBalance(address);

            // Get chain ID
            const chainId = await window.ethereum!.request({
                method: 'eth_chainId'
            });

            const walletInfo: WalletInfo = {
                address,
                balance,
                chainId,
                network: this.getNetworkName(chainId)
            };

            toast.success(`Connected to ${walletInfo.network}`);
            return walletInfo;

        } catch (error: any) {
            console.error('Error connecting to MetaMask:', error);

            if (error.code === 4001) {
                toast.error('Connection rejected by user');
            } else if (error.code === -32002) {
                toast.error('Please check MetaMask - connection request already pending');
            } else {
                toast.error(`Failed to connect: ${error.message || 'Unknown error'}`);
            }

            return null;
        } finally {
            this.isConnecting = false;
        }
    }

    /**
     * Get account balance
     */
    async getBalance(address: string): Promise<string> {
        try {
            const balance = await window.ethereum!.request({
                method: 'eth_getBalance',
                params: [address, 'latest']
            });

            // Convert from wei to ether
            const balanceInEth = parseInt(balance, 16) / Math.pow(10, 18);
            return balanceInEth.toFixed(4);
        } catch (error) {
            console.error('Error getting balance:', error);
            return '0.0000';
        }
    }

    /**
     * Get current account
     */
    async getCurrentAccount(): Promise<string | null> {
        if (!this.isMetaMaskInstalled()) {
            return null;
        }

        try {
            const accounts = await window.ethereum!.request({
                method: 'eth_accounts'
            });

            return accounts.length > 0 ? accounts[0] : null;
        } catch (error) {
            console.error('Error getting current account:', error);
            return null;
        }
    }

    /**
     * Check if wallet is connected
     */
    async isConnected(): Promise<boolean> {
        const account = await this.getCurrentAccount();
        return account !== null;
    }

    /**
     * Disconnect wallet
     */
    async disconnectWallet(): Promise<void> {
        try {
            // Clear any cached connection state
            localStorage.removeItem('walletconnect');
            localStorage.removeItem('metamask_connected');
            sessionStorage.removeItem('wallet_connected');

            // Clear any wallet-related cookies
            if (typeof document !== 'undefined') {
                document.cookie = 'wallet_connected=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
            }

            // For MetaMask, we need to programmatically disconnect
            // This forces the user to reconnect and enter password
            if (this.isMetaMaskInstalled() && window.ethereum) {
                try {
                    // Try to use wallet_revokePermissions if available (newer MetaMask versions)
                    await window.ethereum.request({
                        method: 'wallet_revokePermissions',
                        params: [{ eth_accounts: {} }]
                    });
                } catch (revokeError) {
                    // If revokePermissions is not available, fall back to requesting account disconnection
                    console.log('Revoke permissions not supported, clearing local state');
                }

                // Also try to request account disconnection by asking for empty accounts
                try {
                    await window.ethereum.request({
                        method: 'eth_requestAccounts',
                        params: [{ accounts: [] }]
                    });
                } catch (disconnectError) {
                    // This is expected to fail, but it helps clear some internal state
                    console.log('Account disconnection request handled');
                }
            }

            toast.success('Wallet disconnected. You will need to reconnect and enter your password next time.');
        } catch (error) {
            console.error('Error during disconnect:', error);
            toast.success('Wallet disconnected from application');
        }
    }

    /**
     * Force complete wallet reset - clears all cached connections
     */
    async forceDisconnect(): Promise<void> {
        try {
            // Clear all possible wallet connection caches
            if (typeof window !== 'undefined') {
                localStorage.removeItem('walletconnect');
                localStorage.removeItem('metamask_connected');
                localStorage.removeItem('wallet_connected');
                sessionStorage.removeItem('wallet_connected');
                sessionStorage.removeItem('metamask_connected');

                // Clear cookies
                if (typeof document !== 'undefined') {
                    document.cookie = 'wallet_connected=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
                    document.cookie = 'metamask_connected=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
                }

                // Set disconnect flag
                localStorage.setItem('wallet_disconnected', 'true');
            }

            // Try to revoke permissions
            if (this.isMetaMaskInstalled() && window.ethereum) {
                try {
                    await window.ethereum.request({
                        method: 'wallet_revokePermissions',
                        params: [{ eth_accounts: {} }]
                    });
                } catch (error) {
                    // This is fine if not supported
                    console.log('Revoke permissions not available');
                }
            }

            toast.success('Wallet completely disconnected. MetaMask will ask for password on next connection.');
        } catch (error) {
            console.error('Error during force disconnect:', error);
            toast.success('Wallet disconnected from application');
        }
    }

    /**
     * Switch to a specific network
     */
    async switchNetwork(chainId: string): Promise<boolean> {
        if (!this.isMetaMaskInstalled()) {
            return false;
        }

        try {
            await window.ethereum!.request({
                method: 'wallet_switchEthereumChain',
                params: [{ chainId }]
            });

            toast.success(`Switched to ${this.getNetworkName(chainId)}`);
            return true;
        } catch (error: any) {
            console.error('Error switching network:', error);

            if (error.code === 4902) {
                toast.error('Network not added to MetaMask');
            } else {
                toast.error(`Failed to switch network: ${error.message}`);
            }

            return false;
        }
    }

    /**
     * Add a custom network to MetaMask
     */
    async addNetwork(networkConfig: {
        chainId: string;
        chainName: string;
        nativeCurrency: {
            name: string;
            symbol: string;
            decimals: number;
        };
        rpcUrls: string[];
        blockExplorerUrls?: string[];
    }): Promise<boolean> {
        if (!this.isMetaMaskInstalled()) {
            return false;
        }

        try {
            await window.ethereum!.request({
                method: 'wallet_addEthereumChain',
                params: [networkConfig]
            });

            toast.success(`Added ${networkConfig.chainName} network`);
            return true;
        } catch (error: any) {
            console.error('Error adding network:', error);
            toast.error(`Failed to add network: ${error.message}`);
            return false;
        }
    }

    /**
     * Send a transaction
     */
    async sendTransaction(transactionRequest: TransactionRequest): Promise<string | null> {
        if (!this.isMetaMaskInstalled()) {
            return null;
        }

        try {
            const txHash = await window.ethereum!.request({
                method: 'eth_sendTransaction',
                params: [transactionRequest]
            });

            toast.success('Transaction sent successfully!');
            return txHash;
        } catch (error: any) {
            console.error('Error sending transaction:', error);

            if (error.code === 4001) {
                toast.error('Transaction rejected by user');
            } else {
                toast.error(`Transaction failed: ${error.message}`);
            }

            return null;
        }
    }

    /**
     * Sign a message
     */
    async signMessage(message: string, address: string): Promise<string | null> {
        if (!this.isMetaMaskInstalled()) {
            return null;
        }

        try {
            const signature = await window.ethereum!.request({
                method: 'personal_sign',
                params: [message, address]
            });

            toast.success('Message signed successfully!');
            return signature;
        } catch (error: any) {
            console.error('Error signing message:', error);

            if (error.code === 4001) {
                toast.error('Signature rejected by user');
            } else {
                toast.error(`Signing failed: ${error.message}`);
            }

            return null;
        }
    }

    /**
     * Setup event listeners for account and network changes
     */
    setupEventListeners(
        onAccountsChanged?: (accounts: string[]) => void,
        onChainChanged?: (chainId: string) => void,
        onConnect?: (connectInfo: { chainId: string }) => void,
        onDisconnect?: (error: { code: number; message: string }) => void
    ): void {
        if (!this.isMetaMaskInstalled()) {
            return;
        }

        // Account changes
        if (onAccountsChanged) {
            window.ethereum!.on('accountsChanged', onAccountsChanged);
        }

        // Network changes
        if (onChainChanged) {
            window.ethereum!.on('chainChanged', onChainChanged);
        }

        // Connection
        if (onConnect) {
            window.ethereum!.on('connect', onConnect);
        }

        // Disconnection
        if (onDisconnect) {
            window.ethereum!.on('disconnect', onDisconnect);
        }
    }

    /**
     * Remove event listeners
     */
    removeEventListeners(): void {
        if (!this.isMetaMaskInstalled()) {
            return;
        }

        // Remove all listeners (you might want to be more specific in production)
        window.ethereum!.removeListener('accountsChanged', () => { });
        window.ethereum!.removeListener('chainChanged', () => { });
        window.ethereum!.removeListener('connect', () => { });
        window.ethereum!.removeListener('disconnect', () => { });
    }
}

// Export singleton instance
export const web3Service = Web3Service.getInstance();
export default web3Service;
