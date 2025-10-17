'use client';

import { useState, useEffect } from 'react';

interface KYCDocument {
  document_id: number;
  client_id: number;
  business_name: string;
  client_email: string;
  document_type: string;
  document_name: string;
  file_path: string;
  uploaded_at: string;
  verification_status: string;
}

export default function KYCReview() {
  const [documents, setDocuments] = useState<KYCDocument[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedDoc, setSelectedDoc] = useState<KYCDocument | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [verifying, setVerifying] = useState(false);
  const [adminComments, setAdminComments] = useState('');
  const [rejectionReason, setRejectionReason] = useState('');
  const [actionType, setActionType] = useState<'approve' | 'reject'>('approve');

  useEffect(() => {
    fetchPendingDocuments();
  }, []);

  const fetchPendingDocuments = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('http://localhost:8000/api/v1/onboarding/admin/kyc-review', {
        headers: { 'Authorization': `Bearer ${token}` },
      });

      if (!response.ok) throw new Error('Failed to fetch documents');

      const data = await response.json();
      setDocuments(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleVerification = async () => {
    if (!selectedDoc) return;

    setVerifying(true);
    setError('');

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(
        `http://localhost:8000/api/v1/onboarding/admin/kyc/verify/${selectedDoc.document_id}`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            approved: actionType === 'approve',
            admin_comments: adminComments,
            rejection_reason: actionType === 'reject' ? rejectionReason : null,
          }),
        }
      );

      if (!response.ok) throw new Error('Verification failed');

      await fetchPendingDocuments();
      closeModal();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setVerifying(false);
    }
  };

  const openModal = (doc: KYCDocument, action: 'approve' | 'reject') => {
    setSelectedDoc(doc);
    setActionType(action);
    setShowModal(true);
    setAdminComments('');
    setRejectionReason('');
  };

  const closeModal = () => {
    setShowModal(false);
    setSelectedDoc(null);
    setAdminComments('');
    setRejectionReason('');
  };

  const documentsByClient = documents.reduce((acc, doc) => {
    if (!acc[doc.client_id]) {
      acc[doc.client_id] = {
        business_name: doc.business_name,
        client_email: doc.client_email,
        documents: [],
      };
    }
    acc[doc.client_id].documents.push(doc);
    return acc;
  }, {} as Record<number, { business_name: string; client_email: string; documents: KYCDocument[] }>);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-4 border-red-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">KYC Document Review</h2>
          <p className="text-gray-600 mt-1 font-medium">Review and verify client KYC documents</p>
        </div>
        <div className="bg-red-100 text-red-800 px-4 py-2 rounded-lg font-bold text-lg">
          {documents.length} Pending
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border-2 border-red-200 rounded-lg p-4">
          <p className="text-red-800 font-semibold">{error}</p>
        </div>
      )}

      {Object.keys(documentsByClient).length === 0 ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <p className="text-gray-600 font-medium">No pending KYC documents</p>
        </div>
      ) : (
        <div className="space-y-6">
          {Object.entries(documentsByClient).map(([clientId, clientData]) => (
            <div key={clientId} className="bg-white rounded-lg shadow-lg overflow-hidden">
              <div className="bg-gradient-to-r from-red-500 to-red-600 px-6 py-4">
                <h3 className="text-xl font-bold text-white">{clientData.business_name}</h3>
                <p className="text-red-100 font-medium">{clientData.client_email}</p>
              </div>

              <div className="divide-y divide-gray-200">
                {clientData.documents.map((doc) => (
                  <div key={doc.document_id} className="p-6 hover:bg-gray-50 transition">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <span className="inline-block px-3 py-1 bg-blue-100 text-blue-800 rounded-lg font-bold text-sm">
                            {doc.document_type.replace(/_/g, ' ').toUpperCase()}
                          </span>
                          <span className="inline-block px-3 py-1 bg-yellow-100 text-yellow-800 rounded-lg font-bold text-sm">
                            ⏳ Pending Review
                          </span>
                        </div>
                        <p className="text-lg font-bold text-gray-900 mb-1">{doc.document_name}</p>
                        <p className="text-sm text-gray-600 font-medium">
                          Uploaded: {new Date(doc.uploaded_at).toLocaleString()}
                        </p>
                        <p className="text-sm text-gray-500 font-medium mt-1">
                          File: {doc.file_path}
                        </p>
                      </div>

                      <div className="flex gap-3 ml-4">
                        <button
                          onClick={() => window.open(`http://localhost:8000/${doc.file_path}`, '_blank')}
                          className="px-4 py-2 bg-blue-600 text-white rounded-lg font-bold hover:bg-blue-700 shadow"
                        >
                          View
                        </button>
                        <button
                          onClick={() => openModal(doc, 'approve')}
                          className="px-4 py-2 bg-green-600 text-white rounded-lg font-bold hover:bg-green-700 shadow"
                        >
                          Approve
                        </button>
                        <button
                          onClick={() => openModal(doc, 'reject')}
                          className="px-4 py-2 bg-red-600 text-white rounded-lg font-bold hover:bg-red-700 shadow"
                        >
                          Reject
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {showModal && selectedDoc && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-bold text-gray-900">
                  {actionType === 'approve' ? 'Approve' : 'Reject'} Document
                </h3>
                <button onClick={closeModal} className="text-gray-400 hover:text-gray-600">
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              <div className="bg-gray-50 rounded-lg p-4 mb-6 space-y-2">
                <div><span className="font-bold">Client:</span> {selectedDoc.business_name}</div>
                <div><span className="font-bold">Email:</span> {selectedDoc.client_email}</div>
                <div><span className="font-bold">Document Type:</span> {selectedDoc.document_type.replace(/_/g, ' ').toUpperCase()}</div>
                <div><span className="font-bold">Filename:</span> {selectedDoc.document_name}</div>
                <div><span className="font-bold">Uploaded:</span> {new Date(selectedDoc.uploaded_at).toLocaleString()}</div>
              </div>

              <button
                onClick={() => window.open(`http://localhost:8000/${selectedDoc.file_path}`, '_blank')}
                className="w-full mb-6 px-4 py-3 bg-blue-600 text-white rounded-lg font-bold hover:bg-blue-700 shadow"
              >
                🔍 Open Document in New Tab
              </button>

              <div className="space-y-4 mb-6">
                <div>
                  <label className="block text-sm font-bold text-gray-900 mb-2">
                    Admin Comments
                  </label>
                  <textarea
                    value={adminComments}
                    onChange={(e) => setAdminComments(e.target.value)}
                    rows={3}
                    className="w-full px-3 py-2 text-base border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent font-medium"
                    placeholder="Document verified, information matches, etc."
                  />
                </div>

                {actionType === 'reject' && (
                  <div>
                    <label className="block text-sm font-bold text-gray-900 mb-2">
                      Rejection Reason *
                    </label>
                    <textarea
                      value={rejectionReason}
                      onChange={(e) => setRejectionReason(e.target.value)}
                      rows={3}
                      required
                      className="w-full px-3 py-2 text-base border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent font-medium"
                      placeholder="Document is unclear, information doesn't match, etc."
                    />
                  </div>
                )}
              </div>

              <div className="flex gap-3">
                <button
                  onClick={closeModal}
                  className="flex-1 px-4 py-2 border-2 border-gray-300 rounded-lg hover:bg-gray-50 font-bold"
                >
                  Cancel
                </button>
                <button
                  onClick={handleVerification}
                  disabled={verifying || (actionType === 'reject' && !rejectionReason)}
                  className={`flex-1 px-4 py-2 rounded-lg text-white font-bold shadow ${
                    actionType === 'approve'
                      ? 'bg-green-600 hover:bg-green-700'
                      : 'bg-red-600 hover:bg-red-700'
                  } disabled:bg-gray-400 disabled:cursor-not-allowed`}
                >
                  {verifying ? 'Processing...' : `${actionType === 'approve' ? 'Approve' : 'Reject'} Document`}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}