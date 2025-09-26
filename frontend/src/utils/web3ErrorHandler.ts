/**
 * Web3 Error Handler
 * Provides comprehensive error handling for MetaMask and blockchain interactions
 */

import { toast } from 'react-hot-toast';

export interface Web3Error {
  code: number;
  message: string;
  data?: any;
}

export class Web3ErrorHandler {
  /**
   * Handle MetaMask/Web3 errors with user-friendly messages
   */
  static handleError(error: any): void {
    console.error('Web3 Error:', error);

    // Handle different types of errors
    if (error?.code) {
      switch (error.code) {
        case 4001:
          toast.error('Transaction rejected by user');
          break;
        
        case 4100:
          toast.error('Unauthorized: Please connect to MetaMask');
          break;
        
        case 4200:
          toast.error('Unsupported method');
          break;
        
        case 4900:
          toast.error('MetaMask is disconnected');
          break;
        
        case 4901:
          toast.error('MetaMask is not connected to this site');
          break;
        
        case -32000:
          toast.error('Invalid input or transaction reverted');
          break;
        
        case -32001:
          toast.error('Resource not found');
          break;
        
        case -32002:
          toast.error('Request already pending in MetaMask');
          break;
        
        case -32003:
          toast.error('Transaction underpriced');
          break;
        
        case -32004:
          toast.error('Method not supported');
          break;
        
        case -32005:
          toast.error('Request limit exceeded');
          break;
        
        case -32600:
          toast.error('Invalid JSON-RPC request');
          break;
        
        case -32601:
          toast.error('Method not found');
          break;
        
        case -32602:
          toast.error('Invalid parameters');
          break;
        
        case -32603:
          toast.error('Internal JSON-RPC error');
          break;
        
        default:
          toast.error(`Error ${error.code}: ${error.message || 'Unknown error'}`);
      }
    } else if (error?.message) {
      // Handle specific error messages
      const message = error.message.toLowerCase();
      
      if (message.includes('user rejected')) {
        toast.error('Transaction rejected by user');
      } else if (message.includes('insufficient funds')) {
        toast.error('Insufficient funds for transaction');
      } else if (message.includes('gas')) {
        toast.error('Gas estimation failed or insufficient gas');
      } else if (message.includes('nonce')) {
        toast.error('Transaction nonce error - please reset MetaMask');
      } else if (message.includes('network')) {
        toast.error('Network error - please check your connection');
      } else if (message.includes('timeout')) {
        toast.error('Transaction timeout - please try again');
      } else {
        toast.error(`Error: ${error.message}`);
      }
    } else {
      toast.error('Unknown error occurred');
    }
  }

  /**
   * Get user-friendly error message without showing toast
   */
  static getErrorMessage(error: any): string {
    if (error?.code) {
      switch (error.code) {
        case 4001: return 'Transaction rejected by user';
        case 4100: return 'Unauthorized: Please connect to MetaMask';
        case 4200: return 'Unsupported method';
        case 4900: return 'MetaMask is disconnected';
        case 4901: return 'MetaMask is not connected to this site';
        case -32000: return 'Invalid input or transaction reverted';
        case -32001: return 'Resource not found';
        case -32002: return 'Request already pending in MetaMask';
        case -32003: return 'Transaction underpriced';
        case -32004: return 'Method not supported';
        case -32005: return 'Request limit exceeded';
        default: return `Error ${error.code}: ${error.message || 'Unknown error'}`;
      }
    }

    if (error?.message) {
      const message = error.message.toLowerCase();
      
      if (message.includes('user rejected')) {
        return 'Transaction rejected by user';
      } else if (message.includes('insufficient funds')) {
        return 'Insufficient funds for transaction';
      } else if (message.includes('gas')) {
        return 'Gas estimation failed or insufficient gas';
      } else if (message.includes('nonce')) {
        return 'Transaction nonce error - please reset MetaMask';
      } else if (message.includes('network')) {
        return 'Network error - please check your connection';
      } else if (message.includes('timeout')) {
        return 'Transaction timeout - please try again';
      } else {
        return error.message;
      }
    }

    return 'Unknown error occurred';
  }

  /**
   * Check if error is retryable
   */
  static isRetryableError(error: any): boolean {
    if (error?.code) {
      // These errors can be retried
      const retryableCodes = [-32002, -32003, -32005, -32603];
      return retryableCodes.includes(error.code);
    }

    if (error?.message) {
      const message = error.message.toLowerCase();
      return message.includes('network') || 
             message.includes('timeout') || 
             message.includes('gas') ||
             message.includes('nonce');
    }

    return false;
  }

  /**
   * Check if MetaMask is installed
   */
  static isMetaMaskAvailable(): boolean {
    return typeof window !== 'undefined' && 
           typeof window.ethereum !== 'undefined' && 
           Boolean(window.ethereum.isMetaMask);
  }

  /**
   * Handle MetaMask installation redirect
   */
  static promptMetaMaskInstallation(): void {
    toast.error(
      'MetaMask not detected. Please install MetaMask extension.',
      {
        duration: 5000,
      }
    );
    
    // Open MetaMask download page
    if (typeof window !== 'undefined') {
      window.open('https://metamask.io/download/', '_blank');
    }
  }

  /**
   * Handle network switching errors
   */
  static handleNetworkError(chainId: string, error: any): void {
    console.error('Network switch error:', error);

    if (error?.code === 4902) {
      toast.error('Network not added to MetaMask. Please add it manually.');
    } else if (error?.code === 4001) {
      toast.error('Network switch rejected by user');
    } else {
      toast.error(`Failed to switch network: ${this.getErrorMessage(error)}`);
    }
  }

  /**
   * Handle transaction errors with specific context
   */
  static handleTransactionError(error: any, context?: string): void {
    console.error(`Transaction error${context ? ` (${context})` : ''}:`, error);

    if (error?.code === 4001) {
      toast.error('Transaction cancelled by user');
    } else if (error?.message?.includes('insufficient funds')) {
      toast.error('Insufficient balance to complete transaction');
    } else if (error?.message?.includes('gas')) {
      toast.error('Transaction failed due to gas issues. Try increasing gas limit.');
    } else {
      toast.error(`Transaction failed: ${this.getErrorMessage(error)}`);
    }
  }

  /**
   * Validate address format
   */
  static isValidAddress(address: string): boolean {
    return /^0x[a-fA-F0-9]{40}$/.test(address);
  }

  /**
   * Validate transaction amount
   */
  static isValidAmount(amount: string): boolean {
    const num = parseFloat(amount);
    return !isNaN(num) && num > 0 && num < Infinity;
  }

  /**
   * Get helpful suggestions for common errors
   */
  static getErrorSuggestion(error: any): string | null {
    if (error?.code === -32002) {
      return 'Check MetaMask - you may have a pending request that needs attention.';
    }

    if (error?.code === -32003) {
      return 'Try increasing the gas price in MetaMask settings.';
    }

    if (error?.message?.includes('nonce')) {
      return 'Try resetting your MetaMask account in Settings > Advanced > Reset Account.';
    }

    if (error?.message?.includes('insufficient funds')) {
      return 'Make sure you have enough ETH to cover both the transaction amount and gas fees.';
    }

    return null;
  }
}

export default Web3ErrorHandler;
