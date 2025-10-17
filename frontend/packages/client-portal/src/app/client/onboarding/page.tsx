'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

const KYC_DOCUMENTS = [
  { type: 'rgd_certificate', label: 'Certificate of Incorporation (RGD)', required: true },
  { type: 'tin_certificate', label: 'TIN Certificate', required: true },
  { type: 'vat_certificate', label: 'VAT Certificate', required: false },
  { type: 'ssnit_proof', label: 'SSNIT Registration Proof', required: true },
  { type: 'ghana_card', label: 'Ghana Card (Director)', required: true },
  { type: 'proof_of_address', label: 'Proof of Address (Utility Bill)', required: true },
];

const PAYMENT_INFO = {
  bank: 'GCB Bank',
  accountName: 'Eranos Consulting Services',
  accountNumber: '1234567890',
  branch: 'Accra Main Branch',
  amount: 5150.00,
  currency: 'GHS',
};

interface UploadedDoc {
  type: string;
  file: File;
  preview?: string;
  status?: 'pending' | 'uploading' | 'uploaded' | 'error';
  id?: number;
}

export default function ClientOnboarding() {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [token, setToken] = useState('');
  
  // Step 1: Business Info
  const [businessInfo, setBusinessInfo] = useState({
    businessName: '',
    tinNumber: '',
    vatNumber: '',
    ssnitNumber: '',
  });

  // Step 2: KYC Documents
  const [kycDocuments, setKycDocuments] = useState<UploadedDoc[]>([]);
  const [uploadingKyc, setUploadingKyc] = useState(false);

  // Step 3: Payment
  const [paymentData, setPaymentData] = useState({
    amount: PAYMENT_INFO.amount,
    paymentMethod: 'bank_transfer',
    paymentReference: '',
    description: 'Initial Deposit',
  });
  const [paymentReceipt, setPaymentReceipt] = useState<File | null>(null);
  const [uploadingPayment, setUploadingPayment] = useState(false);

  useEffect(() => {
    const storedToken = localStorage.getItem('token');
    if (!storedToken) {
      router.push('/login');
      return;
    }
    setToken(storedToken);
  }, [router]);

  const handleFileSelect = (type: string, file: File) => {
    // Validate file
    const validTypes = ['application/pdf', 'image/jpeg', 'image/png', 'image/jpg'];
    if (!validTypes.includes(file.type)) {
      setError('Only PDF and image files are allowed');
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      setError('File size must be less than 10MB');
      return;
    }

    setError('');

    // Create preview for images
    let preview: string | undefined;
    if (file.type.startsWith('image/')) {
      preview = URL.createObjectURL(file);
    }

    // Add or update document
    setKycDocuments(prev => {
      const existing = prev.find(doc => doc.type === type);
      if (existing) {
        return prev.map(doc => 
          doc.type === type 
            ? { ...doc, file, preview, status: 'pending' as const }
            : doc
        );
      }
      return [...prev, { type, file, preview, status: 'pending' as const }];
    });
  };

  const uploadKycDocument = async (doc: UploadedDoc) => {
    setUploadingKyc(true);
    
    try {
      const formData = new FormData();
      formData.append('file', doc.file);

      const response = await fetch(
        `http://localhost:8000/api/v1/onboarding/kyc/upload?document_type=${doc.type}`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
          body: formData,
        }
      );

      if (!response.ok) {
        throw new Error('Upload failed');
      }

      const data = await response.json();

      // Update status
      setKycDocuments(prev =>
        prev.map(d => d.type === doc.type ? { ...d, status: 'uploaded' as const, id: data.id } : d)
      );

      return true;
    } catch (err) {
      setKycDocuments(prev =>
        prev.map(d => d.type === doc.type ? { ...d, status: 'error' as const } : d)
      );
      return false;
    } finally {
      setUploadingKyc(false);
    }
  };

  const uploadAllKycDocuments = async () => {
    setUploadingKyc(true);
    setError('');

    const pendingDocs = kycDocuments.filter(doc => doc.status === 'pending');

    for (const doc of pendingDocs) {
      await uploadKycDocument(doc);
    }

    setUploadingKyc(false);
  };

  const handlePaymentUpload = async () => {
    if (!paymentReceipt) {
      setError('Please upload payment receipt');
      return;
    }

    setUploadingPayment(true);
    setError('');

    try {
      const formData = new FormData();
      formData.append('receipt_file', paymentReceipt);

      const response = await fetch(
        `http://localhost:8000/api/v1/onboarding/payment/upload?` +
        `amount=${paymentData.amount}&` +
        `payment_method=${paymentData.paymentMethod}&` +
        `payment_reference=${encodeURIComponent(paymentData.paymentReference)}&` +
        `description=${encodeURIComponent(paymentData.description)}`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
          body: formData,
        }
      );

      if (!response.ok) {
        throw new Error('Payment upload failed');
      }

      // Move to completion step
      setCurrentStep(4);
    } catch (err: any) {
      setError(err.message || 'Payment upload failed');
    } finally {
      setUploadingPayment(false);
    }
  };

  const isStepComplete = (step: number) => {
    switch (step) {
      case 1:
        return businessInfo.businessName && businessInfo.tinNumber;
      case 2:
        const requiredDocs = KYC_DOCUMENTS.filter(d => d.required);
        const uploadedRequired = requiredDocs.every(doc =>
          kycDocuments.some(uploaded => uploaded.type === doc.type && uploaded.status === 'uploaded')
        );
        return uploadedRequired;
      case 3:
        return paymentReceipt !== null;
      default:
        return false;
    }
  };

  const renderStepIndicator = () => (
    <div className="flex items-center justify-center mb-8">
      {[1, 2, 3, 4].map((step) => (
        <div key={step} className="flex items-center">
          <div
            className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold ${
              currentStep === step
                ? 'bg-blue-600 text-white'
                : currentStep > step
                ? 'bg-green-600 text-white'
                : 'bg-gray-300 text-gray-600'
            }`}
          >
            {currentStep > step ? '✓' : step}
          </div>
          {step < 4 && (
            <div className={`w-20 h-1 ${currentStep > step ? 'bg-green-600' : 'bg-gray-300'}`} />
          )}
        </div>
      ))}
    </div>
  );

  const renderStep1 = () => (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-900">Business Information</h2>
      <p className="text-gray-600">Please provide your business details for verification</p>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Business Name *</label>
          <input
            type="text"
            value={businessInfo.businessName}
            onChange={(e) => setBusinessInfo({ ...businessInfo, businessName: e.target.value })}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            placeholder="ABC Company Ltd"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">TIN Number *</label>
          <input
            type="text"
            value={businessInfo.tinNumber}
            onChange={(e) => setBusinessInfo({ ...businessInfo, tinNumber: e.target.value })}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            placeholder="C0000000000"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">VAT Number (if applicable)</label>
          <input
            type="text"
            value={businessInfo.vatNumber}
            onChange={(e) => setBusinessInfo({ ...businessInfo, vatNumber: e.target.value })}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            placeholder="VAT-000000"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">SSNIT Number</label>
          <input
            type="text"
            value={businessInfo.ssnitNumber}
            onChange={(e) => setBusinessInfo({ ...businessInfo, ssnitNumber: e.target.value })}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            placeholder="SSNIT-000000"
          />
        </div>
      </div>

      <button
        onClick={() => setCurrentStep(2)}
        disabled={!isStepComplete(1)}
        className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition disabled:bg-gray-400"
      >
        Continue to KYC Documents
      </button>
    </div>
  );

  const renderStep2 = () => (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-900">KYC Documents</h2>
      <p className="text-gray-600">Upload the required documents for verification</p>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-800 text-sm">
          {error}
        </div>
      )}

      <div className="space-y-4">
        {KYC_DOCUMENTS.map((doc) => {
          const uploaded = kycDocuments.find(d => d.type === doc.type);
          
          return (
            <div key={doc.type} className="border border-gray-200 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <div>
                  <h3 className="font-medium text-gray-900">{doc.label}</h3>
                  {doc.required && <span className="text-xs text-red-600">* Required</span>}
                </div>
                {uploaded && (
                  <span className={`text-xs px-2 py-1 rounded ${
                    uploaded.status === 'uploaded' ? 'bg-green-100 text-green-800' :
                    uploaded.status === 'error' ? 'bg-red-100 text-red-800' :
                    'bg-yellow-100 text-yellow-800'
                  }`}>
                    {uploaded.status}
                  </span>
                )}
              </div>

              {uploaded ? (
                <div className="flex items-center gap-3">
                  <span className="text-sm text-gray-600 flex-1">{uploaded.file.name}</span>
                  {uploaded.status === 'pending' && (
                    <button
                      onClick={() => uploadKycDocument(uploaded)}
                      className="text-blue-600 text-sm hover:underline"
                    >
                      Upload
                    </button>
                  )}
                  <button
                    onClick={() => setKycDocuments(prev => prev.filter(d => d.type !== doc.type))}
                    className="text-red-600 text-sm hover:underline"
                  >
                    Remove
                  </button>
                </div>
              ) : (
                <label className="block">
                  <input
                    type="file"
                    accept=".pdf,.jpg,.jpeg,.png"
                    onChange={(e) => e.target.files && handleFileSelect(doc.type, e.target.files[0])}
                    className="hidden"
                  />
                  <div className="border-2 border-dashed border-gray-300 rounded-lg p-4 text-center cursor-pointer hover:border-blue-500 transition">
                    <svg className="w-8 h-8 text-gray-400 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                    </svg>
                    <p className="text-sm text-gray-600">Click to upload or drag and drop</p>
                    <p className="text-xs text-gray-500 mt-1">PDF, JPG, PNG (Max 10MB)</p>
                  </div>
                </label>
              )}
            </div>
          );
        })}
      </div>

      <div className="flex gap-4">
        <button
          onClick={() => setCurrentStep(1)}
          className="flex-1 bg-gray-200 text-gray-700 py-3 rounded-lg font-semibold hover:bg-gray-300 transition"
        >
          Back
        </button>
        {kycDocuments.some(d => d.status === 'pending') && (
          <button
            onClick={uploadAllKycDocuments}
            disabled={uploadingKyc}
            className="flex-1 bg-green-600 text-white py-3 rounded-lg font-semibold hover:bg-green-700 transition disabled:bg-gray-400"
          >
            {uploadingKyc ? 'Uploading...' : 'Upload All Pending'}
          </button>
        )}
        <button
          onClick={() => setCurrentStep(3)}
          disabled={!isStepComplete(2)}
          className="flex-1 bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition disabled:bg-gray-400"
        >
          Continue to Payment
        </button>
      </div>
    </div>
  );

  const renderStep3 = () => (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-900">Payment Information</h2>
      <p className="text-gray-600">Complete your payment and upload the receipt</p>

      {/* Bank Details */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="font-semibold text-gray-900 mb-4">Bank Transfer Details</h3>
        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-600">Bank:</span>
            <span className="font-medium">{PAYMENT_INFO.bank}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Account Name:</span>
            <span className="font-medium">{PAYMENT_INFO.accountName}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Account Number:</span>
            <span className="font-medium">{PAYMENT_INFO.accountNumber}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Branch:</span>
            <span className="font-medium">{PAYMENT_INFO.branch}</span>
          </div>
          <div className="flex justify-between border-t pt-2 mt-2">
            <span className="text-gray-600">Amount:</span>
            <span className="font-bold text-lg">{PAYMENT_INFO.currency} {PAYMENT_INFO.amount.toLocaleString()}</span>
          </div>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-800 text-sm">
          {error}
        </div>
      )}

      {/* Payment Form */}
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Payment Reference *</label>
          <input
            type="text"
            value={paymentData.paymentReference}
            onChange={(e) => setPaymentData({ ...paymentData, paymentReference: e.target.value })}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            placeholder="Transaction reference number"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Upload Payment Receipt *</label>
          {paymentReceipt ? (
            <div className="flex items-center gap-3 p-4 border border-gray-200 rounded-lg">
              <span className="text-sm text-gray-600 flex-1">{paymentReceipt.name}</span>
              <button
                onClick={() => setPaymentReceipt(null)}
                className="text-red-600 text-sm hover:underline"
              >
                Remove
              </button>
            </div>
          ) : (
            <label className="block">
              <input
                type="file"
                accept=".pdf,.jpg,.jpeg,.png"
                onChange={(e) => e.target.files && setPaymentReceipt(e.target.files[0])}
                className="hidden"
              />
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center cursor-pointer hover:border-blue-500 transition">
                <svg className="w-10 h-10 text-gray-400 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
                <p className="text-sm text-gray-600">Click to upload payment receipt</p>
                <p className="text-xs text-gray-500 mt-1">PDF, JPG, PNG (Max 10MB)</p>
              </div>
            </label>
          )}
        </div>
      </div>

      <div className="flex gap-4">
        <button
          onClick={() => setCurrentStep(2)}
          className="flex-1 bg-gray-200 text-gray-700 py-3 rounded-lg font-semibold hover:bg-gray-300 transition"
        >
          Back
        </button>
        <button
          onClick={handlePaymentUpload}
          disabled={!isStepComplete(3) || uploadingPayment}
          className="flex-1 bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition disabled:bg-gray-400"
        >
          {uploadingPayment ? 'Uploading...' : 'Submit Payment'}
        </button>
      </div>
    </div>
  );

  const renderStep4 = () => (
    <div className="text-center py-8">
      <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
        <svg className="w-10 h-10 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
        </svg>
      </div>
      <h2 className="text-3xl font-bold text-gray-900 mb-4">Onboarding Complete!</h2>
      <p className="text-gray-600 mb-2">
        Your documents and payment have been submitted successfully.
      </p>
      <p className="text-gray-600 mb-8">
        Our team will review your submission within 1-2 business days.
      </p>
      <button
        onClick={() => router.push('/client/dashboard')}
        className="bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700 transition"
      >
        Go to Dashboard
      </button>
    </div>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12 px-4">
      <div className="max-w-3xl mx-auto">
        <div className="bg-white rounded-lg shadow-xl p-8">
          {renderStepIndicator()}
          
          {currentStep === 1 && renderStep1()}
          {currentStep === 2 && renderStep2()}
          {currentStep === 3 && renderStep3()}
          {currentStep === 4 && renderStep4()}
        </div>
      </div>
    </div>
  );
}