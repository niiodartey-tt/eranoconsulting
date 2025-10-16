'use client';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

export default function ClientDashboard() {
  const router = useRouter();
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (!token) return router.push('/login');

    const payload = JSON.parse(atob(token.split('.')[1]));
    setUser(payload);
  }, [router]);

  if (!user) return <p>Loading client dashboard...</p>;

  return (
    <main className="p-10">
      <h1 className="text-3xl font-bold text-gray-800">Client Dashboard</h1>
      <p className="mt-2 text-gray-600">Welcome back, {user.email}</p>
      <p className="text-sm text-gray-500 mt-2">Role: {user.role}</p>
    </main>
  );
}
