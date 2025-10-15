'use client';

import { useEffect } from 'react';
import Cookies from 'js-cookie';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

export default function Dashboard() {
  const router = useRouter();

  useEffect(() => {
    const token = Cookies.get('token');
    if (!token) router.push('/login');
  }, [router]);

  return (
    <main className="min-h-screen bg-gray-100 flex flex-col items-center justify-center">
      <h1 className="text-3xl font-bold text-blue-700 mb-4">Client Dashboard</h1>
      <p className="text-gray-600 mb-6">Welcome to your secure Erano Consulting portal.</p>

      <Link href="/kyc" className="text-blue-600 underline">
        Upload KYC Documents
      </Link>
    </main>
  );
}
