'use client';
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface KYCDocument {
  id: number;
  client_id: number;
  client_name: string;
  client_email: string;
  document_type: string;
  file_name: string;
  file_path: string;
  status: string;
  uploaded_at: string;
}

export default function KYCReviewPage() {
  const [documents, setDocuments] = useState<KYCDocument[]>([]);
  const [selectedDoc, setSelectedDoc] = useState<KYCDocument | null>(null);
  const [loading, setLoading] = useState(true);
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
      }
    } catch (error) {
      console.error(error);
      setMessage('Error loading documents');
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white shadow-sm border-b p-4">
        <div className="max-w-7xl mx-auto flex items-center gap-4">
          <button onClick={() => router.push('/admin/dashboard')} className="text-gray-600">
            Back
          </button>
          <h1 className="text-2xl font-bold">KYC Document Review</h1>
        </div>
      </div>

      <div className="max-w-7xl mx-auto p-8">
        {documents.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-12 text-center">
            <h3 className="text-lg font-medium text-gray-900 mb-2">No Pending Documents</h3>
            <p className="text-gray-500">All KYC documents have been reviewed</p>
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold mb-4">Pending Documents</h2>
            {documents.map((doc) => (
              <div key={doc.id} className="border-b p-4">
                <h3 className="font-semibold">{doc.business_name}</h3>
                <p className="text-sm text-gray-600">{doc.client_email}</p>
                <p className="text-sm">{doc.document_type}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
