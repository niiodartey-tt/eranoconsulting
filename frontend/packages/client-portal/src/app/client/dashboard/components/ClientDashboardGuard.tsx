'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

interface OnboardingStatus {
  client_id: number;
  business_name: string;
  onboarding_status: string;
  kyc_documents_count: number;
  kyc_approved_count: number;
  payment_verified: boolean;
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
      
      // Decode token to check user role
      const payload = JSON.parse(atob(token.split('.')[1]));
      const userRole = payload.role;
      
      // PASSWORD CHANGE CHECK ONLY FOR CLIENTS
      if (userRole === 'client') {
        const passwordChanged = localStorage.getItem('password_changed');
        
        // Check if password needs to be changed
        if (!passwordChanged) {
          router.push('/client/change-password');
          return;
        }
      }
      
      // For admin/staff, skip password check and onboarding check
      if (userRole === 'admin' || userRole === 'staff') {
        setLoading(false);
        return;
      }

      // Check onboarding status (CLIENT ONLY)
      const response = await fetch('http://localhost:8000/api/v1/onboarding/onboarding-status', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) throw new Error('Failed to fetch status');

      const data: OnboardingStatus = await response.json();
      setStatus(data);

      // Redirect based on status
      if (data.onboarding_status === 'pre_active' || data.onboarding_status === 'kyc_submission') {
        router.push('/client/onboarding');
        return;
      }

      if (data.onboarding_status !== 'active') {
        setShowInactive(true);
      }

      setLoading(false);
    } catch (err) {
      console.error('Error checking status:', err);
      setLoading(false);
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
              Your account is currently under review
            </p>
          </div>

          {/* Status Card */}
          <div className="bg-gray-50 rounded-lg p-6 mb-6">
            <h3 className="font-bold text-gray-900 mb-4 text-lg">Current Status</h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-gray-700 font-medium">Business Name:</span>
                <span className="font-bold text-gray-900">{status.business_name}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-700 font-medium">Onboarding Status:</span>
                <span className="inline-block px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full text-sm font-bold">
                  {status.onboarding_status.replace(/_/g, ' ').toUpperCase()}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-700 font-medium">KYC Documents:</span>
                <span className="font-bold text-gray-900">
                  {status.kyc_approved_count} / {status.kyc_documents_count} Approved
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-700 font-medium">Payment:</span>
                <span className={`font-bold ${status.payment_verified ? 'text-green-600' : 'text-red-600'}`}>
                  {status.payment_verified ? '✓ Verified' : '✗ Pending'}
                </span>
              </div>
            </div>
          </div>

          {/* Status Messages */}
          {status.onboarding_status === 'kyc_review' && (
            <div className="bg-blue-50 border-2 border-blue-200 rounded-lg p-4 mb-6">
              <p className="text-blue-900 font-medium">
                📋 Your KYC documents are currently being reviewed by our team. This usually takes 1-2 business days.
              </p>
            </div>
          )}

          {status.onboarding_status === 'payment_review' && (
            <div className="bg-blue-50 border-2 border-blue-200 rounded-lg p-4 mb-6">
              <p className="text-blue-900 font-medium">
                💰 Your payment is being verified. Once confirmed, your account will be activated.
              </p>
            </div>
          )}

          {status.onboarding_status === 'awaiting_signature' && (
            <div className="bg-blue-50 border-2 border-blue-200 rounded-lg p-4 mb-6">
              <p className="text-blue-900 font-medium">
                📝 Your engagement letter is being prepared. You'll receive an email once it's ready for signature.
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