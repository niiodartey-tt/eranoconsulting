'use client';
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

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

export default function KYCReviewPage() {
  const [documents, setDocuments] = useState<KYCDocument[]>([]);
  const [selectedDoc, setSelectedDoc] = useState<KYCDocument | null>(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [notes, setNotes] = useState('');
  const [message, setMessage] = useState('');
  const router = useRouter();

  useEffect(() => {
    fetchPendingDocuments();
  }, []);

  async function fetchPendingDocuments() {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        router.push('/login');
        return;
      }

      const response = await fetch(`${API_URL}/api/v1/onboarding/admin/kyc-review`, {
        headers: { 'Authorization': `Bearer ${token}` },
      });

      if (response.ok) {
        const data = await response.json();
        setDocuments(data);
      } else if (response.status === 401) {
        router.push('/login');
      }
    } catch (error) {
      console.error(error);
      setMessage('Error loading documents');
    } finally {
      setLoading(false);
    }
  }

  async function handleReview(status: 'approved' | 'rejected') {
    if (!selectedDoc) return;
    
    setActionLoading(true);
    setMessage('');

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(
        `${API_URL}/api/v1/onboarding/admin/kyc/${selectedDoc.document_id}/${status}`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ notes }),
        }
      );

      if (response.ok) {
        setMessage(`Document ${status} successfully`);
        setSelectedDoc(null);
        setNotes('');
        fetchPendingDocuments();
      } else {
        const error = await response.json();
        setMessage(`Error: ${error.detail || 'Action failed'}`);
      }
    } catch (error) {
      console.error(error);
      setMessage('Error processing review');
    } finally {
      setActionLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading pending documents...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={() => router.push('/admin/dashboard')}
                className="text-gray-600 hover:text-gray-900"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                </svg>
              </button>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">KYC Document Review</h1>
                <p className="text-sm text-gray-500">Review and approve client documents</p>
              </div>
            </div>
            <span className="bg-yellow-100 text-yellow-800 px-3 py-1 rounded-full text-sm font-medium">
              {documents.length} Pending
            </span>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {message && (
          <div className={`mb-4 p-4 rounded-lg ${
            message.includes('successfully') ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'
          }`}>
            {message}
          </div>
        )}

        {documents.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-12 text-center">
            <svg className="w-16 h-16 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <h3 className="text-lg font-medium text-gray-900 mb-2">No Pending Documents</h3>
            <p className="text-gray-500">All KYC documents have been reviewed</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="space-y-4">
              <h2 className="text-lg font-semibold text-gray-900">Pending Documents</h2>
              {documents.map((doc) => (
                <div
                  key={doc.document_id}
                  onClick={() => setSelectedDoc(doc)}
                  className={`bg-white rounded-lg shadow p-4 cursor-pointer transition ${
                    selectedDoc?.document_id === doc.document_id ? 'ring-2 ring-red-500' : 'hover:shadow-md'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-900">{doc.business_name}</h3>
                      <p className="text-sm text-gray-600">{doc.client_email}</p>
                      <div className="mt-2 flex items-center gap-4 text-xs text-gray-500">
                        <span className="flex items-center gap-1">
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                          </svg>
                          {doc.document_type}
                        </span>
                        <span className="flex items-center gap-1">
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                          {new Date(doc.uploaded_at).toLocaleDateString()}
                        </span>
                      </div>
                    </div>
                    <span className="bg-yellow-100 text-yellow-800 text-xs px-2 py-1 rounded-full">
                      Pending
                    </span>
                  </div>
                </div>
              ))}
            </div>

            <div className="lg:sticky lg:top-4 h-fit">
              {selectedDoc ? (
                <div className="bg-white rounded-lg shadow p-6">
                  <h2 className="text-lg font-semibold text-gray-900 mb-4">Review Document</h2>
                  
                  <div className="space-y-4 mb-6">
                    <div>
                      <label className="text-sm font-medium text-gray-700">Client</label>
                      <p className="text-gray-900">{selectedDoc.business_name}</p>
                      <p className="text-sm text-gray-500">{selectedDoc.client_email}</p>
                    </div>
                    
                    <div>
                      <label className="text-sm font-medium text-gray-700">Document Type</label>
                      <p className="text-gray-900">{selectedDoc.document_type}</p>
                    </div>
                    
                    <div>
                      <label className="text-sm font-medium text-gray-700">File Name</label>
                      <p className="text-gray-900">{selectedDoc.document_name}</p>
                    </div>
                    
                    <div>
                      <label className="text-sm font-medium text-gray-700">Uploaded</label>
                      <p className="text-gray-900">{new Date(selectedDoc.uploaded_at).toLocaleString()}</p>
                    </div>

                    <div>
                      <label className="text-sm font-medium text-gray-700 block mb-2">Preview</label>
                      <div className="border rounded-lg p-4 bg-gray-50">
                        <p className="text-sm text-gray-600 mb-2">Document preview not available</p>
                        <a
                          href={`${API_URL}${selectedDoc.file_path}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-red-600 hover:text-red-700 text-sm font-medium inline-flex items-center gap-1"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                          </svg>
                          Download Document
                        </a>
                      </div>
                    </div>

                    <div>
                      <label className="text-sm font-medium text-gray-700 block mb-2">Review Notes</label>
                      <textarea
                        value={notes}
                        onChange={(e) => setNotes(e.target.value)}
                        className="w-full border border-gray-300 rounded-lg p-3 text-gray-900"
                        rows={4}
                        placeholder="Add notes about this review..."
                      />
                    </div>
                  </div>

                  <div className="flex gap-3">
                    <button
                      onClick={() => handleReview('approved')}
                      disabled={actionLoading}
                      className="flex-1 bg-green-600 text-white py-2 px-4 rounded-lg hover:bg-green-700 transition disabled:bg-gray-400 font-medium"
                    >
                      {actionLoading ? 'Processing...' : 'Approve'}
                    </button>
                    <button
                      onClick={() => handleReview('rejected')}
                      disabled={actionLoading}
                      className="flex-1 bg-red-600 text-white py-2 px-4 rounded-lg hover:bg-red-700 transition disabled:bg-gray-400 font-medium"
                    >
                      {actionLoading ? 'Processing...' : 'Reject'}
                    </button>
                  </div>
                </div>
              ) : (
                <div className="bg-white rounded-lg shadow p-12 text-center">
                  <svg className="w-12 h-12 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 15l-2 5L9 9l11 4-5 2zm0 0l5 5M7.188 2.239l.777 2.897M5.136 7.965l-2.898-.777M13.95 4.05l-2.122 2.122m-5.657 5.656l-2.12 2.122" />
                  </svg>
                  <p className="text-gray-500">Select a document to review</p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}