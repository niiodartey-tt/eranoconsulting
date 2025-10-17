'use client';

import { useState } from 'react';

export default function RegisterPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');

  async function handleRegister(e: React.FormEvent) {
    e.preventDefault();
    setMessage('Registering...');

    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      if (!res.ok) {
        const err = await res.json();
        setMessage(`Error: ${err.detail || 'Registration failed'}`);
        return;
      }

      setMessage('✅ Registration successful! You can now log in.');
    } catch (error) {
      console.error(error);
      setMessage('⚠️ Network error.');
    }
  }

  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-gray-100">
      <div className="bg-white p-8 rounded-2xl shadow-lg w-96">
        <h1 className="text-2xl font-bold text-center mb-4">Create Account</h1>

        <form onSubmit={handleRegister} className="flex flex-col gap-4">
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
            Register
          </button>
        </form>

        <p className="text-center mt-3 text-gray-600">{message}</p>
        <p className="text-center mt-2 text-sm">
          Already have an account? <a href="/login" className="text-blue-600">Login</a>
        </p>
      </div>
    </main>
  );
}
