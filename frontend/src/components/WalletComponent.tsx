/**
 * Wallet Connection Component
 * Provides UI for MetaMask wallet connection and management
 */

'use client';

import React, { useState } from 'react';
import { useWeb3 } from '../hooks/useWeb3';
import { toast } from 'react-hot-toast';

interface WalletComponentProps {
  onConnectionChange?: (isConnected: boolean) => void;
  showBalance?: boolean;
  showNetwork?: boolean;
  className?: string;
}

const WalletComponent: React.FC<WalletComponentProps> = ({
  onConnectionChange,
  showBalance = true,
  showNetwork = true,
  className = ''
}) => {
  const {
    isConnected,
    isConnecting,
    walletInfo,
    error,
    connect,
    disconnect,
    switchNetwork,
    refreshBalance
  } = useWeb3();

  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [showNetworkModal, setShowNetworkModal] = useState(false);

  React.useEffect(() => {
    onConnectionChange?.(isConnected);
  }, [isConnected, onConnectionChange]);

  const formatAddress = (address: string): string => {
    return `${address.slice(0, 6)}...${address.slice(-4)}`;
  };

  const copyAddress = async () => {
    if (walletInfo?.address) {
      try {
        await navigator.clipboard.writeText(walletInfo.address);
        toast.success('Address copied to clipboard!');
      } catch (err) {
        toast.error('Failed to copy address');
      }
    }
  };

  const handleNetworkSwitch = async (chainId: string) => {
    const success = await switchNetwork(chainId);
    if (success) {
      setShowNetworkModal(false);
    }
  };

  const supportedNetworks = [
    { chainId: '0x1', name: 'Ethereum Mainnet' },
    { chainId: '0x89', name: 'Polygon Mainnet' },
    { chainId: '0x38', name: 'BSC Mainnet' },
    { chainId: '0xaa36a7', name: 'Sepolia Testnet' },
    { chainId: '0x13881', name: 'Polygon Mumbai' }
  ];

  if (error) {
    return (
      <div className={`bg-red-50 border border-red-200 rounded-lg p-4 ${className}`}>
        <div className="text-red-800 text-sm">
          <strong>Error:</strong> {error}
        </div>
        <button
          onClick={connect}
          className="mt-2 bg-red-600 text-white px-3 py-1 rounded text-sm hover:bg-red-700 transition-colors"
        >
          Retry Connection
        </button>
      </div>
    );
  }

  if (!isConnected) {
    return (
      <div className={`${className}`}>
        <button
          onClick={connect}
          disabled={isConnecting}
          className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white px-6 py-2 rounded-lg font-medium transition-colors flex items-center gap-2"
        >
          {isConnecting ? (
            <>
              <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                <circle 
                  className="opacity-25" 
                  cx="12" 
                  cy="12" 
                  r="10" 
                  stroke="currentColor" 
                  strokeWidth="4" 
                  fill="none"
                />
                <path 
                  className="opacity-75" 
                  fill="currentColor" 
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                />
              </svg>
              Connecting...
            </>
          ) : (
            <>
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd" />
              </svg>
              Connect Wallet
            </>
          )}
        </button>
      </div>
    );
  }

  return (
    <div className={`relative ${className}`}>
      <button
        onClick={() => setIsDropdownOpen(!isDropdownOpen)}
        className="bg-green-50 hover:bg-green-100 border border-green-200 text-green-800 px-4 py-2 rounded-lg font-medium transition-colors flex items-center gap-3"
      >
        <div className="w-2 h-2 bg-green-500 rounded-full"></div>
        <div className="text-left">
          <div className="text-sm font-medium">
            {formatAddress(walletInfo?.address || '')}
          </div>
          {showBalance && (
            <div className="text-xs text-green-600">
              {walletInfo?.balance} ETH
            </div>
          )}
        </div>
        <svg 
          className={`w-4 h-4 transition-transform ${isDropdownOpen ? 'rotate-180' : ''}`}
          fill="currentColor" 
          viewBox="0 0 20 20"
        >
          <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
        </svg>
      </button>

      {isDropdownOpen && (
        <>
          <div 
            className="fixed inset-0 z-10" 
            onClick={() => setIsDropdownOpen(false)}
          />
          <div className="absolute right-0 mt-2 w-80 bg-white rounded-lg shadow-lg border border-gray-200 z-20">
            <div className="p-4">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold text-gray-900">Wallet Info</h3>
                <button
                  onClick={() => setIsDropdownOpen(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                  </svg>
                </button>
              </div>

              <div className="space-y-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Address
                  </label>
                  <div className="flex items-center gap-2">
                    <code className="text-sm bg-gray-100 px-2 py-1 rounded flex-1">
                      {walletInfo?.address}
                    </code>
                    <button
                      onClick={copyAddress}
                      className="text-blue-600 hover:text-blue-800"
                      title="Copy address"
                    >
                      <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M8 3a1 1 0 011-1h2a1 1 0 110 2H9a1 1 0 01-1-1z" />
                        <path d="M6 3a2 2 0 00-2 2v11a2 2 0 002 2h8a2 2 0 002-2V5a2 2 0 00-2-2 3 3 0 01-3 3H9a3 3 0 01-3-3z" />
                      </svg>
                    </button>
                  </div>
                </div>

                {showBalance && (
                  <div>
                    <div className="flex items-center justify-between mb-1">
                      <label className="block text-sm font-medium text-gray-700">
                        Balance
                      </label>
                      <button
                        onClick={refreshBalance}
                        className="text-xs text-blue-600 hover:text-blue-800"
                      >
                        Refresh
                      </button>
                    </div>
                    <div className="text-lg font-semibold text-green-600">
                      {walletInfo?.balance} ETH
                    </div>
                  </div>
                )}

                {showNetwork && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Network
                    </label>
                    <div className="flex items-center justify-between">
                      <span className="text-sm bg-blue-100 text-blue-800 px-2 py-1 rounded">
                        {walletInfo?.network}
                      </span>
                      <button
                        onClick={() => setShowNetworkModal(true)}
                        className="text-xs text-blue-600 hover:text-blue-800"
                      >
                        Switch
                      </button>
                    </div>
                  </div>
                )}
              </div>

              <div className="mt-4 pt-4 border-t border-gray-200">
                <button
                  onClick={disconnect}
                  className="w-full bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg font-medium transition-colors"
                >
                  Disconnect Wallet
                </button>
              </div>
            </div>
          </div>
        </>
      )}

      {/* Network Switch Modal */}
      {showNetworkModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-96 max-w-90vw">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">Switch Network</h3>
              <button
                onClick={() => setShowNetworkModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                </svg>
              </button>
            </div>

            <div className="space-y-2">
              {supportedNetworks.map((network) => (
                <button
                  key={network.chainId}
                  onClick={() => handleNetworkSwitch(network.chainId)}
                  className={`w-full text-left px-4 py-3 rounded-lg border transition-colors ${
                    walletInfo?.chainId === network.chainId
                      ? 'bg-blue-50 border-blue-200 text-blue-800'
                      : 'hover:bg-gray-50 border-gray-200'
                  }`}
                >
                  <div className="font-medium">{network.name}</div>
                  <div className="text-sm text-gray-500">{network.chainId}</div>
                </button>
              ))}
            </div>

            <div className="mt-4">
              <button
                onClick={() => setShowNetworkModal(false)}
                className="w-full bg-gray-200 hover:bg-gray-300 text-gray-800 px-4 py-2 rounded-lg font-medium transition-colors"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default WalletComponent;
