'use client';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface OnboardingStatus {
  status: string;
  kyc_uploaded: boolean;
  payment_verified: boolean;
  onboarding_completed: boolean;
  engagement_letter_signed: boolean;
  next_step: string;
  message: string;
}

export default function InactiveDashboard() {
  const [status, setStatus] = useState<OnboardingStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    fetchStatus();
    // Poll every 30 seconds for status updates
    const interval = setInterval(fetchStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  async function fetchStatus() {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        router.push('/login');
        return;
      }

      const res = await fetch(`${API_URL}/api/v1/clients/onboarding/status`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!res.ok) throw new Error('Failed to fetch status');

      const data = await res.json();
      setStatus(data);

      // Redirect if status changes to active
      if (data.status === 'active') {
        router.push('/client/dashboard');
      }
    } catch (error) {
      console.error('Error fetching status:', error);
    } finally {
      setLoading(false);
    }
  }

  function handleLogout() {
    localStorage.removeItem('access_token');
    router.push('/login');
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  const getStatusIcon = () => {
    if (status?.status === 'pending_review') {
      return (
        <svg className="w-24 h-24 text-yellow-500 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      );
    } else if (status?.status === 'inactive') {
      return (
        <svg className="w-24 h-24 text-blue-500 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      );
    } else if (status?.status === 'rejected') {
      return (
        <svg className="w-24 h-24 text-red-500 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      );
    }
  };

  const getStatusColor = () => {
    switch (status?.status) {
      case 'pending_review': return 'bg-yellow-50 border-yellow-200';
      case 'inactive': return 'bg-blue-50 border-blue-200';
      case 'rejected': return 'bg-red-50 border-red-200';
      default: return 'bg-gray-50 border-gray-200';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <h1 className="text-2xl font-bold text-gray-900">Eranos Consulting</h1>
            <button
              onClick={handleLogout}
              className="text-gray-600 hover:text-gray-900 transition"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className={`rounded-2xl border-2 p-8 ${getStatusColor()}`}>
          {/* Status Icon */}
          <div className="mb-6">
            {getStatusIcon()}
          </div>

          {/* Status Title */}
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-4">
            {status?.status === 'pending_review' && 'Application Under Review'}
            {status?.status === 'inactive' && 'Documents Verified'}
            {status?.status === 'rejected' && 'Application Requires Attention'}
          </h2>

          {/* Status Message */}
          <p className="text-center text-gray-700 text-lg mb-8">
            {status?.message}
          </p>

          {/* Progress Checklist */}
          <div className="bg-white rounded-xl p-6 shadow-sm mb-6">
            <h3 className="font-bold text-gray-900 mb-4">Onboarding Progress</h3>
            <div className="space-y-3">
              <div className="flex items-center gap-3">
                {status?.kyc_uploaded ? (
                  <svg className="w-6 h-6 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                ) : (
                  <svg className="w-6 h-6 text-gray-300" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                )}
                <span className={status?.kyc_uploaded ? 'text-gray-900' : 'text-gray-500'}>
                  KYC Documents Uploaded
                </span>
              </div>

              <div className="flex items-center gap-3">
                {status?.onboarding_completed ? (
                  <svg className="w-6 h-6 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                ) : (
                  <svg className="w-6 h-6 text-gray-300" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                )}
                <span className={status?.onboarding_completed ? 'text-gray-900' : 'text-gray-500'}>
                  Submitted for Review
                </span>
              </div>

              <div className="flex items-center gap-3">
                {status?.payment_verified ? (
                  <svg className="w-6 h-6 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                ) : (
                  <svg className="w-6 h-6 text-gray-300" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                )}
                <span className={status?.payment_verified ? 'text-gray-900' : 'text-gray-500'}>
                  Payment Verified
                </span>
              </div>

              <div className="flex items-center gap-3">
                {status?.engagement_letter_signed ? (
                  <svg className="w-6 h-6 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                ) : (
                  <svg className="w-6 h-6 text-gray-300" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                )}
                <span className={status?.engagement_letter_signed ? 'text-gray-900' : 'text-gray-500'}>
                  Engagement Letter Signed
                </span>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          {status?.status === 'inactive' && (
            <div className="text-center">
              <button className="bg-blue-600 text-white px-8 py-3 rounded-lg hover:bg-blue-700 transition font-medium">
                Sign Engagement Letter
              </button>
            </div>
          )}

          {status?.status === 'rejected' && (
            <div className="text-center">
              <button 
                onClick={() => router.push('/client/onboarding')}
                className="bg-red-600 text-white px-8 py-3 rounded-lg hover:bg-red-700 transition font-medium"
              >
                Resubmit Documents
              </button>
            </div>
          )}

          {/* Help Text */}
          <div className="mt-8 text-center">
            <p className="text-sm text-gray-600">
              Need assistance? Contact us at{' '}
              <a href="mailto:apexsourceventures@gmail.com" className="text-blue-600 hover:underline">
                apexsourceventures@gmail.com
              </a>
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}