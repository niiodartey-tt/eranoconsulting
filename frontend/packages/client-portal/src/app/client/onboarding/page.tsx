'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

interface UploadedDocument {
  id: number;
  document_type: string;
  document_name: string;
  file_size: number;
  uploaded_at: string;
  verification_status: string;
}

const REQUIRED_DOCUMENTS = [
  { type: 'rgd_certificate', label: 'Certificate of Incorporation (RGD)', description: 'Company registration certificate from Registrar General' },
  { type: 'tin_certificate', label: 'TIN Certificate', description: 'Tax Identification Number certificate' },
  { type: 'ghana_card', label: 'Ghana Card', description: 'National ID of director/owner' },
];

const OPTIONAL_DOCUMENTS = [
  { type: 'vat_certificate', label: 'VAT Certificate', description: 'Value Added Tax registration (if applicable)' },
  { type: 'ssnit_proof', label: 'SSNIT Registration Proof', description: 'Social Security registration' },
  { type: 'proof_of_address', label: 'Proof of Address', description: 'Utility bill or bank statement' },
  { type: 'passport', label: 'Passport', description: 'Alternative to Ghana Card' },
];

export default function KYCUploadWizard() {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState(1);
  const [uploadedDocs, setUploadedDocs] = useState<UploadedDocument[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [uploadingDoc, setUploadingDoc] = useState('');

  useEffect(() => {
    fetchUploadedDocuments();
  }, []);

  const fetchUploadedDocuments = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('http://localhost:8000/api/v1/onboarding/kyc/documents', {
        headers: { 'Authorization': `Bearer ${token}` },
      });

      if (response.ok) {
        const data = await response.json();
        setUploadedDocs(data);
      }
    } catch (err) {
      console.error('Error fetching documents:', err);
    }
  };

  const handleFileUpload = async (documentType: string, file: File) => {
    setError('');
    setUploadingDoc(documentType);

    try {
      const token = localStorage.getItem('access_token');
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(
        `http://localhost:8000/api/v1/onboarding/kyc/upload?document_type=${documentType}`,
        {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${token}` },
          body: formData,
        }
      );

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Upload failed');
      }

      await fetchUploadedDocuments();
    } catch (err: any) {
      setError(err.message || 'Upload failed');
    } finally {
      setUploadingDoc('');
    }
  };

  const isDocumentUploaded = (docType: string) => {
    return uploadedDocs.some(doc => doc.document_type === docType);
  };

  const getDocumentStatus = (docType: string) => {
    return uploadedDocs.find(doc => doc.document_type === docType);
  };

  const allRequiredUploaded = REQUIRED_DOCUMENTS.every(doc => isDocumentUploaded(doc.type));

  const handleSubmitForReview = async () => {
    if (!allRequiredUploaded) {
      setError('Please upload all required documents');
      return;
    }

    setLoading(true);
    try {
      // Just redirect to dashboard - the guard will show pending status
      router.push('/client/dashboard');
    } catch (err: any) {
      setError(err.message);
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-8 px-4">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">KYC Document Upload</h1>
          <p className="text-gray-600 text-lg">Upload required documents to complete your onboarding</p>
        </div>

        {/* Progress Steps */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
          <div className="flex items-center justify-between">
            {[1, 2, 3].map((step) => (
              <div key={step} className="flex items-center flex-1">
                <div className={`flex items-center justify-center w-12 h-12 rounded-full font-bold text-lg ${
                  currentStep >= step ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-600'
                }`}>
                  {step}
                </div>
                {step < 3 && (
                  <div className={`flex-1 h-2 mx-4 rounded ${
                    currentStep > step ? 'bg-blue-600' : 'bg-gray-200'
                  }`} />
                )}
              </div>
            ))}
          </div>
          <div className="flex justify-between mt-4">
            <span className="text-sm font-bold text-gray-700">Required Documents</span>
            <span className="text-sm font-bold text-gray-700">Optional Documents</span>
            <span className="text-sm font-bold text-gray-700">Review & Submit</span>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border-2 border-red-200 rounded-lg p-4 mb-6 flex items-start gap-3">
            <svg className="w-6 h-6 text-red-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p className="text-red-800 font-semibold">{error}</p>
          </div>
        )}

        {/* Step 1: Required Documents */}
        {currentStep === 1 && (
          <div className="bg-white rounded-lg shadow-lg p-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Step 1: Required Documents</h2>
            <p className="text-gray-600 mb-6 font-medium">Please upload the following required documents (PDF or images only, max 10MB)</p>

            <div className="space-y-6">
              {REQUIRED_DOCUMENTS.map((doc) => {
                const uploaded = getDocumentStatus(doc.type);
                return (
                  <div key={doc.type} className="border-2 border-gray-200 rounded-lg p-6 hover:border-blue-300 transition">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex-1">
                        <h3 className="text-lg font-bold text-gray-900 mb-2">{doc.label}</h3>
                        <p className="text-sm text-gray-600 font-medium">{doc.description}</p>
                      </div>
                      {uploaded && (
                        <div className="ml-4">
                          {uploaded.verification_status === 'pending' && (
                            <span className="inline-block px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full text-sm font-bold">
                              ⏳ Pending Review
                            </span>
                          )}
                          {uploaded.verification_status === 'approved' && (
                            <span className="inline-block px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-bold">
                              ✓ Approved
                            </span>
                          )}
                          {uploaded.verification_status === 'rejected' && (
                            <span className="inline-block px-3 py-1 bg-red-100 text-red-800 rounded-full text-sm font-bold">
                              ✗ Rejected
                            </span>
                          )}
                        </div>
                      )}
                    </div>

                    {uploaded ? (
                      <div className="bg-green-50 border-2 border-green-200 rounded-lg p-4 flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                          <div>
                            <p className="font-bold text-green-900">{uploaded.document_name}</p>
                            <p className="text-sm text-green-700 font-medium">
                              {(uploaded.file_size / 1024).toFixed(1)} KB • Uploaded {new Date(uploaded.uploaded_at).toLocaleDateString()}
                            </p>
                          </div>
                        </div>
                        <label className="cursor-pointer px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-bold">
                          Replace
                          <input
                            type="file"
                            className="hidden"
                            accept=".pdf,.jpg,.jpeg,.png"
                            onChange={(e) => {
                              const file = e.target.files?.[0];
                              if (file) handleFileUpload(doc.type, file);
                            }}
                          />
                        </label>
                      </div>
                    ) : (
                      <label className="block cursor-pointer">
                        <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-500 hover:bg-blue-50 transition">
                          {uploadingDoc === doc.type ? (
                            <div className="flex flex-col items-center">
                              <div className="animate-spin rounded-full h-12 w-12 border-b-4 border-blue-600 mb-4"></div>
                              <p className="text-blue-600 font-bold text-lg">Uploading...</p>
                            </div>
                          ) : (
                            <>
                              <svg className="w-12 h-12 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                              </svg>
                              <p className="text-gray-600 font-bold text-lg mb-2">Click to upload or drag and drop</p>
                              <p className="text-sm text-gray-500 font-medium">PDF, JPG, PNG (max 10MB)</p>
                            </>
                          )}
                        </div>
                        <input
                          type="file"
                          className="hidden"
                          accept=".pdf,.jpg,.jpeg,.png"
                          disabled={uploadingDoc === doc.type}
                          onChange={(e) => {
                            const file = e.target.files?.[0];
                            if (file) handleFileUpload(doc.type, file);
                          }}
                        />
                      </label>
                    )}
                  </div>
                );
              })}
            </div>

            <div className="flex justify-end mt-8">
              <button
                onClick={() => setCurrentStep(2)}
                disabled={!allRequiredUploaded}
                className="px-8 py-3 bg-blue-600 text-white rounded-lg font-bold text-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed shadow-lg"
              >
                Next: Optional Documents →
              </button>
            </div>
          </div>
        )}

        {/* Step 2: Optional Documents */}
        {currentStep === 2 && (
          <div className="bg-white rounded-lg shadow-lg p-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Step 2: Optional Documents</h2>
            <p className="text-gray-600 mb-6 font-medium">Upload additional documents if applicable (you can skip this step)</p>

            <div className="space-y-6">
              {OPTIONAL_DOCUMENTS.map((doc) => {
                const uploaded = getDocumentStatus(doc.type);
                return (
                  <div key={doc.type} className="border-2 border-gray-200 rounded-lg p-6">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex-1">
                        <h3 className="text-lg font-bold text-gray-900 mb-2">{doc.label}</h3>
                        <p className="text-sm text-gray-600 font-medium">{doc.description}</p>
                      </div>
                      {uploaded && (
                        <span className="ml-4 inline-block px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-bold">
                          ✓ Uploaded
                        </span>
                      )}
                    </div>

                    {uploaded ? (
                      <div className="bg-green-50 border-2 border-green-200 rounded-lg p-4 flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                          <p className="font-bold text-green-900">{uploaded.document_name}</p>
                        </div>
                      </div>
                    ) : (
                      <label className="block cursor-pointer">
                        <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-blue-500 hover:bg-blue-50 transition">
                          {uploadingDoc === doc.type ? (
                            <div className="flex items-center justify-center">
                              <div className="animate-spin rounded-full h-8 w-8 border-b-4 border-blue-600 mr-3"></div>
                              <p className="text-blue-600 font-bold">Uploading...</p>
                            </div>
                          ) : (
                            <p className="text-gray-600 font-bold">Click to upload</p>
                          )}
                        </div>
                        <input
                          type="file"
                          className="hidden"
                          accept=".pdf,.jpg,.jpeg,.png"
                          disabled={uploadingDoc === doc.type}
                          onChange={(e) => {
                            const file = e.target.files?.[0];
                            if (file) handleFileUpload(doc.type, file);
                          }}
                        />
                      </label>
                    )}
                  </div>
                );
              })}
            </div>

            <div className="flex justify-between mt-8">
              <button
                onClick={() => setCurrentStep(1)}
                className="px-8 py-3 border-2 border-gray-300 text-gray-700 rounded-lg font-bold text-lg hover:bg-gray-50"
              >
                ← Back
              </button>
              <button
                onClick={() => setCurrentStep(3)}
                className="px-8 py-3 bg-blue-600 text-white rounded-lg font-bold text-lg hover:bg-blue-700 shadow-lg"
              >
                Next: Review & Submit →
              </button>
            </div>
          </div>
        )}

        {/* Step 3: Review & Submit */}
        {currentStep === 3 && (
          <div className="bg-white rounded-lg shadow-lg p-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Step 3: Review & Submit</h2>

            {/* Summary */}
            <div className="bg-blue-50 border-2 border-blue-200 rounded-lg p-6 mb-6">
              <h3 className="font-bold text-blue-900 text-lg mb-4">Document Summary</h3>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-blue-800 font-medium">Required Documents:</p>
                  <p className="text-2xl font-bold text-blue-900">{uploadedDocs.filter(d => REQUIRED_DOCUMENTS.some(r => r.type === d.document_type)).length} / {REQUIRED_DOCUMENTS.length}</p>
                </div>
                <div>
                  <p className="text-sm text-blue-800 font-medium">Optional Documents:</p>
                  <p className="text-2xl font-bold text-blue-900">{uploadedDocs.filter(d => OPTIONAL_DOCUMENTS.some(o => o.type === d.document_type)).length}</p>
                </div>
              </div>
            </div>

            {/* Uploaded Documents List */}
            <div className="space-y-3 mb-8">
              <h3 className="font-bold text-gray-900 text-lg mb-4">Uploaded Documents</h3>
              {uploadedDocs.map((doc) => (
                <div key={doc.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg border-2 border-gray-200">
                  <div className="flex items-center gap-3">
                    <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <div>
                      <p className="font-bold text-gray-900">{doc.document_name}</p>
                      <p className="text-sm text-gray-600 font-medium">{doc.document_type.replace(/_/g, ' ').toUpperCase()}</p>
                    </div>
                  </div>
                  <span className="text-sm text-gray-500 font-medium">{(doc.file_size / 1024).toFixed(1)} KB</span>
                </div>
              ))}
            </div>

            {/* Info Box */}
            <div className="bg-yellow-50 border-2 border-yellow-200 rounded-lg p-6 mb-8">
              <h4 className="font-bold text-yellow-900 mb-3 text-lg">📋 What Happens Next?</h4>
              <ol className="list-decimal list-inside space-y-2 text-yellow-900 font-medium">
                <li>Your documents will be reviewed by our admin team (1-2 business days)</li>
                <li>You'll receive email notifications about the review status</li>
                <li>After approval, you'll need to submit your payment</li>
                <li>Once payment is verified, your account will be activated</li>
              </ol>
            </div>

            {/* Action Buttons */}
            <div className="flex justify-between">
              <button
                onClick={() => setCurrentStep(2)}
                className="px-8 py-3 border-2 border-gray-300 text-gray-700 rounded-lg font-bold text-lg hover:bg-gray-50"
              >
                ← Back
              </button>
              <button
                onClick={handleSubmitForReview}
                disabled={loading || !allRequiredUploaded}
                className="px-8 py-3 bg-green-600 text-white rounded-lg font-bold text-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed shadow-lg"
              >
                {loading ? 'Submitting...' : 'Submit for Review ✓'}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}