'use client';

import { useState, useEffect } from 'react';

interface PendingRegistration {
  id: number;
  user_id: number;
  email: string;
  full_name: string;
  business_name: string;
  phone: string;
  services_requested: string[];
  registration_date: string;
  onboarding_status: string;
}

export default function PendingRegistrations() {
  const [registrations, setRegistrations] = useState<PendingRegistration[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedRegistration, setSelectedRegistration] = useState<PendingRegistration | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [approving, setApproving] = useState(false);
  const [adminNotes, setAdminNotes] = useState('');
  const [rejectionReason, setRejectionReason] = useState('');
  const [actionType, setActionType] = useState<'approve' | 'reject'>('approve');
  const [tempPassword, setTempPassword] = useState('');

  useEffect(() => {
    fetchRegistrations();
  }, []);

  const fetchRegistrations = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('http://localhost:8000/api/v1/onboarding/admin/pending-registrations', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) throw new Error('Failed to fetch registrations');

      const data = await response.json();
      setRegistrations(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleVerification = async () => {
    if (!selectedRegistration) return;

    setApproving(true);
    setError('');

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(
        `http://localhost:8000/api/v1/onboarding/admin/verify-registration/${selectedRegistration.id}`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            approved: actionType === 'approve',
            admin_notes: adminNotes,
            rejection_reason: actionType === 'reject' ? rejectionReason : null,
          }),
        }
      );

      if (!response.ok) throw new Error('Verification failed');

      const data = await response.json();
      
      if (actionType === 'approve') {
        setTempPassword(data.temp_password);
      }

      // Refresh the list
      await fetchRegistrations();
      
      // Reset form if rejecting, keep modal open if approving to show password
      if (actionType === 'reject') {
        setShowModal(false);
        setSelectedRegistration(null);
        setAdminNotes('');
        setRejectionReason('');
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setApproving(false);
    }
  };

  const openModal = (registration: PendingRegistration, action: 'approve' | 'reject') => {
    setSelectedRegistration(registration);
    setActionType(action);
    setShowModal(true);
    setTempPassword('');
    setAdminNotes('');
    setRejectionReason('');
  };

  const closeModal = () => {
    setShowModal(false);
    setSelectedRegistration(null);
    setTempPassword('');
    setAdminNotes('');
    setRejectionReason('');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Pending Registrations</h2>
          <p className="text-gray-600 mt-1">Review and approve new client registrations</p>
        </div>
        <div className="bg-red-100 text-red-800 px-4 py-2 rounded-lg font-bold text-lg">
          {registrations.length} Pending
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {/* Registrations List */}
      {registrations.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <p className="text-gray-600">No pending registrations</p>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Business
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Contact
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Services
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Date
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {registrations.map((registration) => (
                <tr key={registration.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div>
                      <div className="text-sm font-medium text-gray-900">
                        {registration.business_name}
                      </div>
                      <div className="text-sm text-gray-500">ID: {registration.id}</div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm text-gray-900">{registration.full_name}</div>
                    <div className="text-sm text-gray-500">{registration.email}</div>
                    <div className="text-sm text-gray-500">{registration.phone}</div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex flex-wrap gap-1">
                      {registration.services_requested.map((service, idx) => (
                        <span
                          key={idx}
                          className="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded"
                        >
                          {service.replace(/_/g, ' ')}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(registration.registration_date).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <button
                      onClick={() => openModal(registration, 'approve')}
                      className="text-green-600 hover:text-green-900 mr-4"
                    >
                      Approve
                    </button>
                    <button
                      onClick={() => openModal(registration, 'reject')}
                      className="text-red-600 hover:text-red-900"
                    >
                      Reject
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Verification Modal */}
      {showModal && selectedRegistration && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              {/* Modal Header */}
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-bold text-gray-900">
                  {actionType === 'approve' ? 'Approve' : 'Reject'} Registration
                </h3>
                <button onClick={closeModal} disabled={approving} className="text-gray-400 hover:text-gray-600">
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              {/* Registration Details */}
              <div className="bg-gray-50 rounded-lg p-4 mb-6 space-y-2">
                <div className="text-base"><span className="font-bold text-gray-900">Business:</span> <span className="font-semibold text-gray-800">{selectedRegistration.business_name}</span></div>
                <div className="text-base"><span className="font-bold text-gray-900">Contact:</span> <span className="font-semibold text-gray-800">{selectedRegistration.full_name}</span></div>
                <div className="text-base"><span className="font-bold text-gray-900">Email:</span> <span className="font-semibold text-gray-800">{selectedRegistration.email}</span></div>
                <div className="text-base"><span className="font-bold text-gray-900">Phone:</span> <span className="font-semibold text-gray-800">{selectedRegistration.phone}</span></div>
              </div>

              {/* Temporary Password Display (after approval) */}
              {tempPassword && (
                <div className="bg-green-50 border-2 border-green-300 rounded-lg p-6 mb-6">
                  <h4 className="font-bold text-green-900 text-lg mb-3">✅ Registration Approved!</h4>
                  <p className="text-sm text-green-800 mb-4 font-medium">
                    Temporary password has been sent to the client's email:
                  </p>
                  <div className="bg-white rounded-lg p-4 border-2 border-green-400">
                    <p className="text-xs text-gray-600 mb-2 font-semibold uppercase">Temporary Password</p>
                    <div className="font-mono text-2xl font-bold text-center text-gray-900 tracking-wider">
                      {tempPassword}
                    </div>
                  </div>
                  <p className="text-sm text-green-800 mt-4 font-medium">
                    ⚠️ Client will be required to change this password on first login before accessing the dashboard.
                  </p>
                </div>
              )}

              {/* Form Fields */}
              {!tempPassword && (
                <>
                  <div className="space-y-4 mb-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Admin Notes
                      </label>
                      <textarea
                        value={adminNotes}
                        onChange={(e) => setAdminNotes(e.target.value)}
                        rows={3}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                        placeholder="Phone verification completed, documents verified, etc."
                      />
                    </div>

                    {actionType === 'reject' && (
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Rejection Reason *
                        </label>
                        <textarea
                          value={rejectionReason}
                          onChange={(e) => setRejectionReason(e.target.value)}
                          rows={3}
                          required
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                          placeholder="Please provide a reason for rejection..."
                        />
                      </div>
                    )}
                  </div>

                  {/* Action Buttons */}
                  <div className="flex gap-3">
                    <button
                      onClick={closeModal}
                      className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                      disabled={approving} // ADD THIS LINE
                    >
                      Cancel
                    </button>
                    <button
                      onClick={handleVerification}
                      disabled={approving || (actionType === 'reject' && !rejectionReason)}
                      className={`flex-1 px-4 py-2 rounded-lg text-white font-semibold ${
                        actionType === 'approve'
                          ? 'bg-green-600 hover:bg-green-700'
                          : 'bg-red-600 hover:bg-red-700'
                      } disabled:bg-gray-400 disabled:cursor-not-allowed`}
                    >
                      {approving ? 'Processing...' : `${actionType === 'approve' ? 'Approve' : 'Reject'} Registration`}
                    </button>
                  </div>
                </>
              )}

              {/* Close Button (after approval) */}
              {tempPassword && (
                <button
                  onClick={closeModal}
                  className="w-full px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                >
                  Close
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}