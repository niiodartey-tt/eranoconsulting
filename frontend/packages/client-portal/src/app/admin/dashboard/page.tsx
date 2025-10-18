'use client';
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Messages from '../../../client/dashboard/components/Messages';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface User {
  id: number;
  email: string;
  full_name?: string;
  role: string;
}

export default function AdminDashboard() {
  const [user, setUser] = useState<User | null>(null);
  const [showMessages, setShowMessages] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);
  const router = useRouter();

  useEffect(() => {
    fetchUser();
    fetchUnreadCount();
    const interval = setInterval(fetchUnreadCount, 30000);
    return () => clearInterval(interval);
  }, []);

  async function fetchUser() {
    try {
      const token = localStorage.getItem('access_token');
      const res = await fetch(`${API_URL}/api/v1/users/me`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setUser(data);
      }
    } catch (error) {
      console.error('Error fetching user:', error);
    }
  }

  async function fetchUnreadCount() {
    try {
      const token = localStorage.getItem('access_token');
      const res = await fetch(`${API_URL}/api/v1/messages/unread-count`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setUnreadCount(data.unread_count);
      }
    } catch (error) {
      console.error('Error fetching unread count:', error);
    }
  }

  function handleLogout() {
    localStorage.removeItem('access_token');
    router.push('/login');
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Admin Dashboard</h1>
              <p className="text-sm text-gray-600">Welcome back, {user?.full_name || user?.email}</p>
            </div>
            <button
              onClick={handleLogout}
              className="px-4 py-2 text-gray-600 hover:text-gray-900 transition"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        {/* ✨ NEW SECTION: Quick Actions */}
        <div className="mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Quick Actions</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            
            {/* User Management */}
            <button 
              onClick={() => router.push('/admin/users')}
              className="bg-white rounded-xl p-6 shadow-md hover:shadow-lg transition border-l-4 border-purple-500 text-left"
            >
              <div className="flex items-center gap-4">
                <div className="bg-purple-100 p-3 rounded-lg">
                  <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                  </svg>
                </div>
                <div>
                  <h3 className="font-bold text-gray-900">Manage Users</h3>
                  <p className="text-sm text-gray-600">Create & manage staff accounts</p>
                </div>
              </div>
            </button>

            {/* Client Management */}
            <button 
              onClick={() => router.push('/admin/clients')}
              className="bg-white rounded-xl p-6 shadow-md hover:shadow-lg transition border-l-4 border-blue-500 text-left"
            >
              <div className="flex items-center gap-4">
                <div className="bg-blue-100 p-3 rounded-lg">
                  <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                  </svg>
                </div>
                <div>
                  <h3 className="font-bold text-gray-900">Client Management</h3>
                  <p className="text-sm text-gray-600">View & manage all clients</p>
                </div>
              </div>
            </button>

            {/* KYC Review Queue */}
            <button 
              onClick={() => router.push('/admin/kyc-review')}
              className="bg-white rounded-xl p-6 shadow-md hover:shadow-lg transition border-l-4 border-yellow-500 text-left"
            >
              <div className="flex items-center gap-4">
                <div className="bg-yellow-100 p-3 rounded-lg">
                  <svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <h3 className="font-bold text-gray-900">KYC Review Queue</h3>
                    <span className="bg-yellow-500 text-white text-xs font-bold px-2 py-1 rounded-full">3</span>
                  </div>
                  <p className="text-sm text-gray-600">Review pending documents</p>
                </div>
              </div>
            </button>

          </div>
        </div>

        {/* Stats Dashboard */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-xl p-6 shadow-md hover:shadow-lg transition border-t-4 border-blue-500">
            <div className="flex items-center justify-between mb-4">
              <div className="bg-blue-100 p-3 rounded-lg">
                <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                </svg>
              </div>
              <span className="text-2xl font-bold text-gray-900">42</span>
            </div>
            <h3 className="text-gray-600 font-medium">Total Clients</h3>
            <p className="text-sm text-gray-500 mt-1">8 active this month</p>
          </div>

          <div className="bg-white rounded-xl p-6 shadow-md hover:shadow-lg transition border-t-4 border-green-500">
            <div className="flex items-center justify-between mb-4">
              <div className="bg-green-100 p-3 rounded-lg">
                <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <span className="text-2xl font-bold text-gray-900">5</span>
            </div>
            <h3 className="text-gray-600 font-medium">Active Projects</h3>
            <p className="text-sm text-gray-500 mt-1">All systems operational</p>
          </div>

          <div className="bg-white rounded-xl p-6 shadow-md hover:shadow-lg transition border-t-4 border-yellow-500">
            <div className="flex items-center justify-between mb-4">
              <div className="bg-yellow-100 p-3 rounded-lg">
                <svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>
              <span className="text-2xl font-bold text-gray-900">3</span>
            </div>
            <h3 className="text-gray-600 font-medium">Pending Reviews</h3>
            <p className="text-sm text-gray-500 mt-1">Require approval</p>
          </div>

          <div 
            className="bg-white rounded-xl p-6 shadow-md hover:shadow-lg transition border-t-4 border-purple-500 cursor-pointer"
            onClick={() => setShowMessages(true)}
          >
            <div className="flex items-center justify-between mb-4">
              <div className="bg-purple-100 p-3 rounded-lg">
                <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                </svg>
              </div>
              <div className="text-right">
                <span className="text-2xl font-bold text-gray-900">7</span>
                {unreadCount > 0 && (
                  <span className="ml-2 bg-red-500 text-white text-xs font-bold px-2 py-1 rounded-full">
                    {unreadCount}
                  </span>
                )}
              </div>
            </div>
            <h3 className="text-gray-600 font-medium">Messages</h3>
            <p className="text-sm text-gray-500 mt-1">
              {unreadCount > 0 ? `${unreadCount} unread` : 'All caught up'}
            </p>
          </div>
        </div>

        {/* Client Onboarding Pipeline */}
        <div className="bg-white rounded-xl p-6 shadow-md mb-8">
          <h3 className="text-lg font-bold text-gray-900 mb-4">Client Onboarding Pipeline</h3>
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            <div className="text-center p-4 bg-gray-50 rounded-lg cursor-pointer hover:bg-gray-100 transition">
              <div className="text-3xl font-bold text-gray-900">2</div>
              <div className="text-sm text-gray-600 mt-1">Pre-Active</div>
              <div className="text-xs text-gray-500 mt-1">New accounts</div>
            </div>
            <div 
              onClick={() => router.push('/admin/kyc-review')}
              className="text-center p-4 bg-blue-50 rounded-lg cursor-pointer hover:bg-blue-100 transition"
            >
              <div className="text-3xl font-bold text-blue-600">3</div>
              <div className="text-sm text-gray-600 mt-1">Pending Review</div>
              <div className="text-xs text-gray-500 mt-1">KYC submitted</div>
            </div>
            <div className="text-center p-4 bg-yellow-50 rounded-lg cursor-pointer hover:bg-yellow-100 transition">
              <div className="text-3xl font-bold text-yellow-600">2</div>
              <div className="text-sm text-gray-600 mt-1">Inactive</div>
              <div className="text-xs text-gray-500 mt-1">Awaiting signature</div>
            </div>
            <div className="text-center p-4 bg-green-50 rounded-lg cursor-pointer hover:bg-green-100 transition">
              <div className="text-3xl font-bold text-green-600">35</div>
              <div className="text-sm text-gray-600 mt-1">Active</div>
              <div className="text-xs text-gray-500 mt-1">Fully onboarded</div>
            </div>
            <div className="text-center p-4 bg-red-50 rounded-lg cursor-pointer hover:bg-red-100 transition">
              <div className="text-3xl font-bold text-red-600">1</div>
              <div className="text-sm text-gray-600 mt-1">Rejected</div>
              <div className="text-xs text-gray-500 mt-1">Needs resubmit</div>
            </div>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="bg-white rounded-xl p-6 shadow-md">
          <h3 className="text-lg font-bold text-gray-900 mb-4">Recent Activity</h3>
          <div className="space-y-4">
            <div className="flex items-center gap-4 p-3 bg-gray-50 rounded-lg">
              <div className="bg-blue-100 p-2 rounded-lg">
                <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-900">New KYC submission from ABC Ltd</p>
                <p className="text-xs text-gray-500">5 minutes ago</p>
              </div>
            </div>

            <div className="flex items-center gap-4 p-3 bg-gray-50 rounded-lg">
              <div className="bg-green-100 p-2 rounded-lg">
                <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-900">Payment verified for XYZ Corp</p>
                <p className="text-xs text-gray-500">1 hour ago</p>
              </div>
            </div>

            <div className="flex items-center gap-4 p-3 bg-gray-50 rounded-lg">
              <div className="bg-purple-100 p-2 rounded-lg">
                <svg className="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
              </div>
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-900">New staff account created</p>
                <p className="text-xs text-gray-500">3 hours ago</p>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Messages Modal */}
      {showMessages && (
        <Messages 
          onClose={() => {
            setShowMessages(false);
            fetchUnreadCount();
          }} 
          currentUserId={user?.id || 0} 
        />
      )}
    </div>
  );
}