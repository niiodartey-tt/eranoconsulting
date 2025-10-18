'use client';
import { useState } from 'react';
import axios from 'axios';

export default function KycUploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!file) {
      setStatus('Please select a file first.');
      return;
    }

    const token = localStorage.getItem('access_token');
    if (!token) {
      setStatus('❌ No auth token found. Please log in first.');
      return;
    }

    setIsLoading(true);
    setStatus('Uploading...');

    try {
      const formData = new FormData();
      formData.append('file', file);

      // Upload the file
      const res = await axios.post(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/onboarding/upload`,
        formData,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
          timeout: 30000,
        }
      );

      if (res.status === 200 || res.status === 201) {
        setStatus('✅ File uploaded successfully!');
        setFile(null);
        
        // ✨ NEW: Mark KYC as uploaded
        await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/clients/onboarding/mark-kyc-uploaded`, {
          method: 'PUT',
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        
        // ✨ NEW: Option to submit for review
        setStatus('✅ File uploaded! Click "Submit for Review" when all documents are ready.');
      }
    } catch (err: any) {
      // ... existing error handling ...
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen items-center justify-center bg-gray-50 p-4">
      <div className="bg-white p-8 rounded-xl shadow-md w-full max-w-2xl">
        <h2 className="text-2xl font-bold mb-6 text-center">KYC Upload</h2>
        
        {/* Auth Status Warning */}
        {typeof window !== 'undefined' && !localStorage.getItem('access_token') && (
          <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded-md">
            <p className="text-sm text-yellow-800">
              ⚠️ <strong>Not authenticated.</strong> You need to log in first.
            </p>
          </div>
        )}

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Select Document
            </label>
            <input
              type="file"
              onChange={(e) => {
                setFile(e.target.files?.[0] || null);
                setStatus('');
              }}
              className="w-full border border-gray-300 p-2 rounded-md text-sm"
              disabled={isLoading}
              accept="image/*,.pdf"
            />
            {file && (
              <p className="text-xs text-gray-500 mt-1">
                {file.name} ({(file.size / 1024).toFixed(1)} KB)
              </p>
            )}
          </div>

          <button
            onClick={handleSubmit}
            disabled={!file || isLoading}
            className="w-full bg-blue-600 text-white py-2 rounded-md hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors font-medium"
          >
            {isLoading ? 'Uploading...' : 'Upload'}
          </button>

          {status && (
            <div className={`mt-4 p-3 rounded-md text-sm ${
              status.includes('✅') 
                ? 'bg-green-50 text-green-800 border border-green-200' 
                : 'bg-red-50 text-red-800 border border-red-200'
            }`}>
              {status}
            </div>
          )}
        </div>


      </div>
    </main>
  );
}