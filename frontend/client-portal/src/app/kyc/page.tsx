'use client';

import { useState } from 'react';
import Cookies from 'js-cookie';
import axios from 'axios';

export default function KycUploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      setStatus('Please select a file first.');
      return;
    }

    const token = Cookies.get('token');
    if (!token) {
      setStatus('Not authenticated.');
      return;
    }

    try {
      const formData = new FormData();
      formData.append('file', file);

      const res = await axios.post(
        `${process.env.NEXT_PUBLIC_API_URL}/client/kyc`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (res.status === 200 || res.status === 201) {
        setStatus('✅ File uploaded successfully.');
      }
    } catch (err: any) {
      console.error(err);
      setStatus('❌ Upload failed.');
    }
  };

  return (
    <main className="flex min-h-screen items-center justify-center bg-gray-50">
      <form
        onSubmit={handleSubmit}
        className="bg-white p-8 rounded-xl shadow-md w-96 text-center"
      >
        <h2 className="text-2xl font-bold mb-6">KYC Upload</h2>
        <input
          type="file"
          onChange={(e) => setFile(e.target.files?.[0] || null)}
          className="w-full border p-2 mb-4"
        />
        <button
          type="submit"
          className="w-full bg-blue-600 text-white py-2 rounded-md hover:bg-blue-700"
        >
          Upload
        </button>
        {status && <p className="mt-4 text-sm">{status}</p>}
      </form>
    </main>
  );
}
