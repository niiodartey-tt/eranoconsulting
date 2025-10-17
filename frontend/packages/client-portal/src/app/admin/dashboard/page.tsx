'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import PendingRegistrations from './components/PendingRegistrations';
import KYCReview from './components/KYCReview';
import Messages from './components/Messages';

interface User {
  id: number;
  email: string;
  full_name: string;
  role: string;
}

export default function AdminDashboard() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [pendingCount, setPendingCount] = useState(0);


  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      router.push('/login');
      return;
    }

    fetchUserData(token);
  }, [router]);

  // Add useEffect to fetch count
  useEffect(() => {
    const fetchPendingCount = async () => {
      try {
        const token = localStorage.getItem('access_token');
        const response = await fetch('http://localhost:8000/api/v1/onboarding/admin/pending-registrations', {
          headers: { 'Authorization': `Bearer ${token}` },
        });
        if (response.ok) {
          const data = await response.json();
          setPendingCount(data.length);
        }
      } catch (err) {
        console.error('Error fetching pending count:', err);
      }
    };
    
    fetchPendingCount();
    // Refresh every 30 seconds
    const interval = setInterval(fetchPendingCount, 30000);
    return () => clearInterval(interval);
  }, []);


  const fetchUserData = async (token: string) => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/users/me', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch user data');
      }

      const data = await response.json();
      
      if (data.role !== 'admin') {
        router.push('/login');
        return;
      }

      setUser(data);
    } catch (error) {
      console.error('Error:', error);
      localStorage.removeItem('access_token');
      router.push('/login');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    router.push('/login');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-red-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-red-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-red-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Admin Dashboard</h1>
              <p className="text-sm text-gray-600 font-medium">Welcome back, {user?.full_name}</p>
            </div>
            <button
              onClick={handleLogout}
              className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 font-bold"
            >
              Logout
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Tabs */}
        <div className="bg-white rounded-lg shadow mb-6">
          <div className="border-b border-gray-200">
            <nav className="flex -mb-px">
              <button
                onClick={() => setActiveTab('overview')}
                className={`px-6 py-4 text-sm font-bold border-b-2 transition ${
                  activeTab === 'overview'
                    ? 'border-red-600 text-red-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                📊 Overview
              </button>
              <button
                onClick={() => setActiveTab('registrations')}
                className={`px-6 py-4 text-sm font-bold border-b-2 relative ${
                  activeTab === 'registrations'
                    ? 'border-red-600 text-red-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Pending Registrations
                {pendingCount > 0 && (
                  <span className="ml-2 inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-white bg-red-600 rounded-full">
                    {pendingCount}
                  </span>
                )}
              </button>
              <button
                onClick={() => setActiveTab('kyc')}
                className={`px-6 py-4 text-sm font-bold border-b-2 transition ${
                  activeTab === 'kyc'
                    ? 'border-red-600 text-red-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                🔍 KYC Review
              </button>
              <button
                onClick={() => setActiveTab('messages')}
                className={`px-6 py-4 text-sm font-bold border-b-2 transition ${
                  activeTab === 'messages'
                    ? 'border-red-600 text-red-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                💬 Messages
              </button>
            </nav>
          </div>
        </div>

        {/* Tab Content */}
        <div>
          {activeTab === 'overview' && (
            <div className="bg-white rounded-lg shadow p-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">Dashboard Overview</h2>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* Quick Stats */}
                <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg p-6 text-white">
                  <h3 className="text-sm font-semibold mb-2 opacity-90">Total Clients</h3>
                  <p className="text-4xl font-bold">12</p>
                </div>

                <div className="bg-gradient-to-br from-yellow-500 to-yellow-600 rounded-lg p-6 text-white">
                  <h3 className="text-sm font-semibold mb-2 opacity-90">Pending Reviews</h3>
                  <p className="text-4xl font-bold">5</p>
                </div>

                <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-lg p-6 text-white">
                  <h3 className="text-sm font-semibold mb-2 opacity-90">Active Clients</h3>
                  <p className="text-4xl font-bold">8</p>
                </div>
              </div>

              <div className="mt-8 bg-blue-50 border-2 border-blue-200 rounded-lg p-6">
                <h3 className="font-bold text-blue-900 text-lg mb-3">Quick Actions</h3>
                <div className="space-y-2">
                  <button
                    onClick={() => setActiveTab('registrations')}
                    className="w-full text-left px-4 py-3 bg-white rounded-lg hover:bg-blue-100 transition font-semibold text-gray-900"
                  >
                    → Review Pending Registrations
                  </button>
                  <button
                    onClick={() => setActiveTab('kyc')}
                    className="w-full text-left px-4 py-3 bg-white rounded-lg hover:bg-blue-100 transition font-semibold text-gray-900"
                  >
                    → Review KYC Documents
                  </button>
                  <button
                    onClick={() => setActiveTab('messages')}
                    className="w-full text-left px-4 py-3 bg-white rounded-lg hover:bg-blue-100 transition font-semibold text-gray-900"
                  >
                    → View Messages
                  </button>
                </div>
              </div>
            </div>
          )}
          
          {activeTab === 'registrations' && <PendingRegistrations />}
          
          {activeTab === 'kyc' && <KYCReview />}
          
          {activeTab === 'messages' && <Messages />}
        </div>
      </div>
    </div>
  );
}