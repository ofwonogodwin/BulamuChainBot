'use client';

import React, { createContext, useContext, useReducer, useEffect, ReactNode } from 'react';
import { toast } from 'react-hot-toast';
import Cookies from 'js-cookie';
import { authService } from '@/services/api';

// Types
export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  user_type: 'patient' | 'doctor' | 'admin';
  phone_number?: string;
  is_verified?: boolean;
}

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

type AuthAction =
  | { type: 'AUTH_START' }
  | { type: 'AUTH_SUCCESS'; payload: User }
  | { type: 'AUTH_ERROR'; payload: string }
  | { type: 'AUTH_LOGOUT' }
  | { type: 'CLEAR_ERROR' };

interface AuthContextType extends AuthState {
  login: (email: string, password: string) => Promise<boolean>;
  register: (userData: any) => Promise<boolean>;
  logout: () => void;
  clearError: () => void;
  refreshAuth: () => Promise<void>;
}

// Initial state
const initialState: AuthState = {
  user: null,
  isAuthenticated: false,
  isLoading: true,
  error: null,
};

// Reducer
const authReducer = (state: AuthState, action: AuthAction): AuthState => {
  switch (action.type) {
    case 'AUTH_START':
      return { ...state, isLoading: true, error: null };
    case 'AUTH_SUCCESS':
      return {
        ...state,
        user: action.payload,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      };
    case 'AUTH_ERROR':
      return {
        ...state,
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: action.payload,
      };
    case 'AUTH_LOGOUT':
      return {
        ...state,
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: null,
      };
    case 'CLEAR_ERROR':
      return { ...state, error: null };
    default:
      return state;
  }
};

// Context
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Provider component
export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);

  // Check for existing token on mount
  useEffect(() => {
    const checkAuth = async () => {
      const token = Cookies.get('access_token');
      if (token) {
        try {
          const response = await authService.getCurrentUser();
          if (response.success && response.data) {
            dispatch({ type: 'AUTH_SUCCESS', payload: response.data });
          } else {
            // Token exists but invalid
            Cookies.remove('access_token');
            Cookies.remove('refresh_token');
            dispatch({ type: 'AUTH_LOGOUT' });
          }
        } catch (error) {
          console.error('Auth check error:', error);
          Cookies.remove('access_token');
          Cookies.remove('refresh_token');
          dispatch({ type: 'AUTH_LOGOUT' });
        }
      } else {
        dispatch({ type: 'AUTH_LOGOUT' });
      }
    };

    checkAuth();
  }, []);

  // Login function
  const login = async (usernameOrEmail: string, password: string): Promise<boolean> => {
    dispatch({ type: 'AUTH_START' });

    try {
      // Try to determine if input is email or username
      const isEmail = usernameOrEmail.includes('@');
      let loginData;

      if (isEmail) {
        // If email provided, we need to find the username first
        // For now, let's try using email as username (we might need to adjust backend)
        loginData = { username: usernameOrEmail, password };
      } else {
        loginData = { username: usernameOrEmail, password };
      }

      const response = await authService.login(loginData);

      if (response.success && response.data) {
        // Store tokens
        Cookies.set('access_token', response.data.access, { expires: 1 }); // 1 day
        Cookies.set('refresh_token', response.data.refresh, { expires: 7 }); // 7 days

        // Get user profile
        const userResponse = await authService.getCurrentUser();
        if (userResponse.success && userResponse.data) {
          dispatch({ type: 'AUTH_SUCCESS', payload: userResponse.data });
          toast.success('Welcome back!');
          return true;
        }
      }

      dispatch({ type: 'AUTH_ERROR', payload: response.message || 'Login failed' });
      toast.error(response.message || 'Login failed');
      return false;
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.response?.data?.message || error.message || 'Login failed';
      dispatch({ type: 'AUTH_ERROR', payload: errorMessage });
      toast.error(errorMessage);
      return false;
    }
  };

  // Register function
  const register = async (userData: any): Promise<boolean> => {
    dispatch({ type: 'AUTH_START' });

    try {
      const response = await authService.register(userData);

      if (response.success) {
        toast.success('Registration successful! Please check your email for verification.');
        dispatch({ type: 'AUTH_LOGOUT' });
        return true;
      }

      dispatch({ type: 'AUTH_ERROR', payload: response.message || 'Registration failed' });
      toast.error(response.message || 'Registration failed');
      return false;
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || error.message || 'Registration failed';
      dispatch({ type: 'AUTH_ERROR', payload: errorMessage });
      toast.error(errorMessage);
      return false;
    }
  };

  // Logout function
  const logout = () => {
    Cookies.remove('access_token');
    Cookies.remove('refresh_token');
    dispatch({ type: 'AUTH_LOGOUT' });
    toast.success('Logged out successfully');
  };

  // Clear error function
  const clearError = () => {
    dispatch({ type: 'CLEAR_ERROR' });
  };

  // Refresh auth function
  const refreshAuth = async (): Promise<void> => {
    const token = Cookies.get('access_token');
    if (token) {
      try {
        const response = await authService.getCurrentUser();
        if (response.success && response.data) {
          dispatch({ type: 'AUTH_SUCCESS', payload: response.data });
        }
      } catch (error) {
        console.error('Auth refresh error:', error);
      }
    }
  };

  const contextValue: AuthContextType = {
    ...state,
    login,
    register,
    logout,
    clearError,
    refreshAuth,
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
};

// Hook to use auth context
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
