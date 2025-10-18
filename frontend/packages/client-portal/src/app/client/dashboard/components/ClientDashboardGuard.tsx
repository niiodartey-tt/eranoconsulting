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

export default function ClientDashboardGuard({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [status, setStatus] = useState<OnboardingStatus | null>(null);
  const [showInactive, setShowInactive] = useState(false);

  useEffect(() => {
    checkOnboardingStatus();
  }, []);

  const checkOnboardingStatus = async () => {
    try {
      const token = localStorage.getItem('access_token');
      
      if (!token) {
        router.push('/login');
        return;
      }

      // Decode token to check user role
      const payload = JSON.parse(atob(token.split('.')[1]));
      const userRole = payload.role;
      
      // For admin/staff, skip onboarding check
      if (userRole === 'admin' || userRole === 'staff') {
        setLoading(false);
        return;
      }

      // Check onboarding status (CLIENT ONLY)
      const response = await fetch(`${API_URL}/api/v1/clients/onboarding/status`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        console.error('Failed to fetch status');
        setLoading(false);
        return; // Allow access anyway if endpoint fails
      }

      const data: OnboardingStatus = await response.json();
      setStatus(data);

      // Redirect based on status
      if (data.status === 'pre_active') {
        router.push('/client/onboarding');
        return;
      }

      if (data.status === 'pending_review' || data.status === 'inactive') {
        setShowInactive(true);
      }

      setLoading(false);
    } catch (err) {
      console.error('Error checking status:', err);
      setLoading(false); // Allow access anyway if error
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-blue-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600 font-medium">Checking your account status...</p>
        </div>
      </div>
    );
  }

  if (showInactive && status) {
    return (
      <div className="min-h-screen bg-blue-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full p-8">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="w-20 h-20 bg-yellow-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-10 h-10 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h2 className="text-3xl font-bold text-gray-900 mb-2">Account Pending Activation</h2>
            <p className="text-gray-600 text-lg">
              {status.message}
            </p>
          </div>

          {/* Status Card */}
          <div className="bg-gray-50 rounded-lg p-6 mb-6">
            <h3 className="font-bold text-gray-900 mb-4 text-lg">Current Status</h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-gray-700 font-medium">Onboarding Status:</span>
                <span className="inline-block px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full text-sm font-bold">
                  {status.status.replace(/_/g, ' ').toUpperCase()}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-700 font-medium">KYC Documents:</span>
                <span className={`font-bold ${status.kyc_uploaded ? 'text-green-600' : 'text-gray-600'}`}>
                  {status.kyc_uploaded ? '✓ Uploaded' : '○ Not Uploaded'}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-700 font-medium">Payment:</span>
                <span className={`font-bold ${status.payment_verified ? 'text-green-600' : 'text-gray-600'}`}>
                  {status.payment_verified ? '✓ Verified' : '○ Pending'}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-700 font-medium">Engagement Letter:</span>
                <span className={`font-bold ${status.engagement_letter_signed ? 'text-green-600' : 'text-gray-600'}`}>
                  {status.engagement_letter_signed ? '✓ Signed' : '○ Pending'}
                </span>
              </div>
            </div>
          </div>

          {/* Status Messages */}
          {status.status === 'pending_review' && (
            <div className="bg-blue-50 border-2 border-blue-200 rounded-lg p-4 mb-6">
              <p className="text-blue-900 font-medium">
                📋 Your documents are currently being reviewed by our team. This usually takes 1-2 business days.
              </p>
            </div>
          )}

          {status.status === 'inactive' && (
            <div className="bg-blue-50 border-2 border-blue-200 rounded-lg p-4 mb-6">
              <p className="text-blue-900 font-medium">
                📝 Your documents have been verified. Please sign the engagement letter to activate your account.
              </p>
            </div>
          )}

          {/* Next Steps */}
          <div className="bg-green-50 border-2 border-green-200 rounded-lg p-4">
            <h4 className="font-bold text-green-900 mb-2 text-lg">What Happens Next?</h4>
            <ol className="list-decimal list-inside space-y-2 text-green-800 font-medium">
              <li>Admin reviews your KYC documents</li>
              <li>Payment verification completed</li>
              <li>Engagement letter issued for signature</li>
              <li>Account activated - Full dashboard access granted!</li>
            </ol>
          </div>

          {/* Logout Button */}
          <button
            onClick={() => {
              localStorage.clear();
              router.push('/login');
            }}
            className="w-full mt-6 px-4 py-3 border-2 border-gray-300 rounded-lg hover:bg-gray-50 font-bold text-gray-700"
          >
            Logout
          </button>
        </div>
      </div>
    );
  }

  // Account is active, show dashboard
  return <>{children}</>;
}