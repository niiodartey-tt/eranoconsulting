// Secure authentication utilities
import axios, { AxiosInstance } from 'axios';
import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

// Types
interface User {
  id: number;
  email: string;
  role: 'admin' | 'staff' | 'client';
  fullName?: string;
  isVerified: boolean;
}

interface AuthState {
  user: User | null;
  accessToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  setAuth: (user: User, token: string) => void;
  clearAuth: () => void;
  setLoading: (loading: boolean) => void;
}

// Secure token storage using sessionStorage (not localStorage)
class SecureTokenStorage {
  private static readonly TOKEN_KEY = 'auth_token';
  private static readonly CSRF_KEY = 'csrf_token';
  
  static setToken(token: string): void {
    // Store in memory for this session only
    sessionStorage.setItem(this.TOKEN_KEY, token);
  }
  
  static getToken(): string | null {
    return sessionStorage.getItem(this.TOKEN_KEY);
  }
  
  static clearToken(): void {
    sessionStorage.removeItem(this.TOKEN_KEY);
    sessionStorage.removeItem(this.CSRF_KEY);
  }
  
  static setCSRFToken(token: string): void {
    sessionStorage.setItem(this.CSRF_KEY, token);
  }
  
  static getCSRFToken(): string | null {
    return sessionStorage.getItem(this.CSRF_KEY);
  }
}

// Create auth store
export const useAuthStore = create<AuthState>()(
  devtools(
    persist(
      (set) => ({
        user: null,
        accessToken: null,
        isAuthenticated: false,
        isLoading: false,
        
        setAuth: (user, token) => {
          SecureTokenStorage.setToken(token);
          set({
            user,
            accessToken: token,
            isAuthenticated: true,
            isLoading: false,
          });
        },
        
        clearAuth: () => {
          SecureTokenStorage.clearToken();
          set({
            user: null,
            accessToken: null,
            isAuthenticated: false,
            isLoading: false,
          });
        },
        
        setLoading: (loading) => set({ isLoading: loading }),
      }),
      {
        name: 'auth-storage',
        partialize: (state) => ({ user: state.user }), // Only persist user, not token
      }
    )
  )
);

// API Client with interceptors
export class ApiClient {
  private client: AxiosInstance;
  
  constructor(baseURL: string) {
    this.client = axios.create({
      baseURL,
      withCredentials: true, // Send cookies
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    this.setupInterceptors();
  }
  
  private setupInterceptors(): void {
    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        const token = SecureTokenStorage.getToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        
        const csrfToken = SecureTokenStorage.getCSRFToken();
        if (csrfToken) {
          config.headers['X-CSRF-Token'] = csrfToken;
        }
        
        return config;
      },
      (error) => Promise.reject(error)
    );
    
    // Response interceptor
    this.client.interceptors.response.use(
      (response) => {
        // Extract CSRF token from response if present
        const csrfToken = response.headers['x-csrf-token'];
        if (csrfToken) {
          SecureTokenStorage.setCSRFToken(csrfToken);
        }
        
        return response;
      },
      async (error) => {
        const originalRequest = error.config;
        
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;
          
          try {
            // Attempt to refresh token
            const response = await this.refreshToken();
            const { access_token } = response.data;
            
            SecureTokenStorage.setToken(access_token);
            originalRequest.headers.Authorization = `Bearer ${access_token}`;
            
            return this.client(originalRequest);
          } catch (refreshError) {
            // Refresh failed, clear auth and redirect to login
            useAuthStore.getState().clearAuth();
            window.location.href = '/login';
            return Promise.reject(refreshError);
          }
        }
        
        return Promise.reject(error);
      }
    );
  }
  
  private async refreshToken() {
    return this.client.post('/api/v1/auth/refresh');
  }
  
  public getClient(): AxiosInstance {
    return this.client;
  }
}

// Create singleton API client
export const apiClient = new ApiClient(
  process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
);

// Auth service
export class AuthService {
  static async login(email: string, password: string) {
    const response = await apiClient.getClient().post('/api/v1/auth/login', {
      username: email, // OAuth2PasswordRequestForm expects 'username'
      password,
    });
    
    const { access_token, user } = response.data;
    useAuthStore.getState().setAuth(user, access_token);
    
    return response.data;
  }
  
  static async logout() {
    try {
      await apiClient.getClient().post('/api/v1/auth/logout');
    } finally {
      useAuthStore.getState().clearAuth();
    }
  }
  
  static async register(data: {
    email: string;
    password: string;
    fullName?: string;
  }) {
    const response = await apiClient.getClient().post('/api/v1/auth/register', data);
    return response.data;
  }
  
  static async getCurrentUser() {
    const response = await apiClient.getClient().get('/api/v1/users/me');
    return response.data;
  }
  
  static async verifyEmail(token: string) {
    const response = await apiClient.getClient().post('/api/v1/auth/verify-email', {
      token,
    });
    return response.data;
  }
  
  static isAuthenticated(): boolean {
    return useAuthStore.getState().isAuthenticated;
  }
  
  static getUser(): User | null {
    return useAuthStore.getState().user;
  }
}
