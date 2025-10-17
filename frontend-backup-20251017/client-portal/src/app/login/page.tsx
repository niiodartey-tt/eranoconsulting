'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');
  const router = useRouter();

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    setMessage('Logging in...');

    try {
      const body = new URLSearchParams();
      body.append('username', email);
      body.append('password', password);

      if (res.ok) {
        const data = await res.json();
        localStorage.setItem("access_token", data.access_token);

        // Decode the JWT to get the role
        const payload = JSON.parse(atob(data.access_token.split(".")[1]));
        const role = payload.role || "client";

        if (role === "admin") router.push("/admin/dashboard");
        else if (role === "staff") router.push("/staff/dashboard");
        else router.push("/client/dashboard");
      }

      if (!res.ok) {
        const err = await res.json();
        setMessage(`❌ ${err.detail || 'Login failed'}`);
        return;
      }

      const data = await res.json();
      localStorage.setItem('access_token', data.access_token);
      setMessage('✅ Login successful!');
      router.push('/dashboard');
    } catch (error) {
      console.error(error);
      setMessage('⚠️ Network error.');
    }
  }

  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-gray-100">
      <div className="bg-white p-8 rounded-2xl shadow-lg w-96">
        <h1 className="text-2xl font-bold text-center mb-4">Sign In</h1>

        <form onSubmit={handleLogin} className="flex flex-col gap-4">
          <input
            type="email"
            placeholder="Email"
            className="border p-2 rounded"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />

          <input
            type="password"
            placeholder="Password"
            className="border p-2 rounded"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />

          <button type="submit" className="bg-blue-600 text-white py-2 rounded hover:bg-blue-700">
            Login
          </button>
        </form>

        <p className="text-center mt-3 text-gray-600">{message}</p>
        <p className="text-center mt-2 text-sm">
          No account? <a href="/register" className="text-blue-600">Register</a>
        </p>
      </div>
    </main>
  );
}
