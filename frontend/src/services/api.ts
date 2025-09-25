import axios from 'axios';
import Cookies from 'js-cookie';

// API Configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001/api';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = Cookies.get('access_token');
  if (token) {
    config.headers = config.headers || {};
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// API Response interface
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  errors?: any;
}

// Helper function for API calls
const makeApiCall = async <T = any>(
  endpoint: string,
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' = 'GET',
  data?: any,
  config?: any
): Promise<ApiResponse<T>> => {
  try {
    let response;
    switch (method) {
      case 'GET':
        response = await api.get(endpoint, config);
        break;
      case 'POST':
        response = await api.post(endpoint, data, config);
        break;
      case 'PUT':
        response = await api.put(endpoint, data, config);
        break;
      case 'DELETE':
        response = await api.delete(endpoint, config);
        break;
      default:
        throw new Error(`Unsupported method: ${method}`);
    }

    return {
      success: true,
      data: response.data as T,
    };
  } catch (error: any) {
    console.error('API Error:', error);
    const message = error.response?.data?.detail ||
      error.response?.data?.message ||
      error.message ||
      'An error occurred';
    return {
      success: false,
      message,
      errors: error.response?.data,
    };
  }
};

// Authentication Service
export const authService = {
  login: (credentials: { username: string; password: string }) =>
    makeApiCall('/auth/login/', 'POST', credentials),

  register: (userData: {
    email: string;
    username: string;
    password: string;
    password_confirm: string;
    first_name: string;
    last_name: string;
    user_type: string;
    phone_number?: string;
  }) => makeApiCall('/auth/register/', 'POST', userData),

  logout: () => makeApiCall('/auth/logout/', 'POST'),

  getCurrentUser: () => makeApiCall('/auth/profile/'),

  updateProfile: (data: any) => makeApiCall('/auth/profile/', 'PUT', data),

  changePassword: (data: { old_password: string; new_password: string }) =>
    makeApiCall('/auth/change-password/', 'POST', data),

  requestPasswordReset: (email: string) =>
    makeApiCall('/auth/password-reset/request/', 'POST', { email }),

  resetPassword: (data: { token: string; password: string }) =>
    makeApiCall('/auth/password-reset/confirm/', 'POST', data),

  verifyEmail: (token: string) =>
    makeApiCall('/auth/verify-email/', 'POST', { token }),

  resendVerification: () =>
    makeApiCall('/auth/resend-verification/', 'POST'),
};

// Consultation Service
export const consultationService = {
  getConsultations: (params?: { page?: number; status?: string }) =>
    makeApiCall('/consultations/', 'GET', undefined, { params }),

  getConsultation: (id: string) =>
    makeApiCall(`/consultations/${id}/`),

  createConsultation: (data: {
    symptoms: string;
    language?: string;
    urgency_level?: string;
  }) => makeApiCall('/consultations/', 'POST', data),

  sendMessage: (consultationId: string, message: string) =>
    makeApiCall(`/consultations/${consultationId}/messages/`, 'POST', { message }),

  getMessages: (consultationId: string) =>
    makeApiCall(`/consultations/${consultationId}/messages/`),

  endConsultation: (id: string) =>
    makeApiCall(`/consultations/${id}/end/`, 'POST'),

  getEmergencyAlerts: () =>
    makeApiCall('/consultations/emergency-alerts/'),
};

// Medical Records Service
export const recordsService = {
  getRecords: (params?: { page?: number; record_type?: string }) =>
    makeApiCall('/records/', 'GET', undefined, { params }),

  getRecord: (id: string) =>
    makeApiCall(`/records/${id}/`),

  createRecord: (data: FormData) =>
    makeApiCall('/records/', 'POST', data, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),

  updateRecord: (id: string, data: any) =>
    makeApiCall(`/records/${id}/`, 'PUT', data),

  deleteRecord: (id: string) =>
    makeApiCall(`/records/${id}/`, 'DELETE'),

  shareRecord: (id: string, doctorEmail: string, permissions: string[]) =>
    makeApiCall(`/records/${id}/share/`, 'POST', { doctor_email: doctorEmail, permissions }),

  getSharedRecords: () =>
    makeApiCall('/records/shared/'),

  getPatientProfile: () =>
    makeApiCall('/records/patient-profile/'),

  updatePatientProfile: (data: any) =>
    makeApiCall('/records/patient-profile/', 'PUT', data),

  getAccessLogs: (recordId?: string) =>
    makeApiCall('/records/access-logs/', 'GET', undefined, {
      params: recordId ? { record_id: recordId } : {}
    }),
};

// Blockchain Service
export const blockchainService = {
  getTransactions: (params?: { page?: number; transaction_type?: string }) =>
    makeApiCall('/blockchain/transactions/', 'GET', undefined, { params }),

  getTransaction: (id: string) =>
    makeApiCall(`/blockchain/transactions/${id}/`),

  verifyMedicine: (medicineId: string, batchId?: string) =>
    makeApiCall('/blockchain/verify-medicine/', 'POST', { medicine_id: medicineId, batch_id: batchId }),

  getMedicineHistory: (medicineId: string) =>
    makeApiCall(`/blockchain/medicine-history/${medicineId}/`),

  reportCounterfeit: (data: {
    medicine_id: string;
    description: string;
    location?: string;
  }) => makeApiCall('/blockchain/report-counterfeit/', 'POST', data),

  getNetworkStatus: () =>
    makeApiCall('/blockchain/network-status/'),
};

// Language Service
export const languageService = {
  translate: (text: string, targetLanguage: string) =>
    makeApiCall('/language/translate/', 'POST', { text, target_language: targetLanguage }),

  getSupportedLanguages: () =>
    makeApiCall('/language/supported/'),

  detectLanguage: (text: string) =>
    makeApiCall('/language/detect/', 'POST', { text }),

  getTranslationHistory: () =>
    makeApiCall('/language/history/'),
};

// File Upload Service
export const fileService = {
  uploadFile: (file: File, type: string = 'document') => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('type', type);

    return makeApiCall('/files/upload/', 'POST', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },

  deleteFile: (fileId: string) =>
    makeApiCall(`/files/${fileId}/`, 'DELETE'),

  getFileInfo: (fileId: string) =>
    makeApiCall(`/files/${fileId}/`),
};

// Analytics Service
export const analyticsService = {
  getDashboardStats: () =>
    makeApiCall('/analytics/dashboard/'),

  getConsultationStats: (period?: string) =>
    makeApiCall('/analytics/consultations/', 'GET', undefined, {
      params: period ? { period } : {}
    }),

  getHealthTrends: () =>
    makeApiCall('/analytics/health-trends/'),
};

export default api;
