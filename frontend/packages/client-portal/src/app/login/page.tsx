'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    setMessage('');
    setIsLoading(true);
    setMessage('Logging in...');

    try {
      const body = new URLSearchParams();
      body.append('username', email);
      body.append('password', password);

      const res = await fetch(`${API_URL}/api/v1/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: body.toString(),
      });

      // Check if response is JSON
      const contentType = res.headers.get('content-type');
      if (!contentType || !contentType.includes('application/json')) {
        setMessage('❌ Backend error: Server returned HTML instead of JSON. Is the backend running?');
        setIsLoading(false);
        return;
      }

      if (!res.ok) {
        const err = await res.json();
        setMessage(`❌ ${err.detail || 'Login failed'}`);
        setIsLoading(false);
        return;
      }

      const data = await res.json();
      localStorage.setItem('access_token', data.access_token);

      // Decode the JWT to get the role
      const payload = JSON.parse(atob(data.access_token.split('.')[1]));
      const role = payload.role || 'client';

      setMessage('✅ Login successful!');

      // Redirect based on role
      setTimeout(() => {
        if (role === 'admin') router.push('/admin/dashboard');
        else if (role === 'staff') router.push('/staff/dashboard');
        else router.push('/client/dashboard');
      }, 1000);

    } catch (error) {
      console.error('Login error:', error);
      setMessage('⚠️ Cannot connect to backend. Please ensure the backend server is running on port 8000.');
      setIsLoading(false);
    }
  }

  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="bg-white p-8 rounded-2xl shadow-2xl w-full max-w-md">
        <div className="text-center mb-6">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">Welcome Back</h1>
          <p className="text-gray-600 text-sm">Sign in to your Eranos account</p>
        </div>

        <form onSubmit={handleLogin} className="flex flex-col gap-4">
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
              Email Address
            </label>
            <input
              id="email"
              type="email"
              placeholder="you@example.com"
              className="w-full border border-gray-300 p-3 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition text-gray-900 placeholder-gray-400"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
              Password
            </label>
            <input
              id="password"
              type="password"
              placeholder="Enter your password"
              className="w-full border border-gray-300 p-3 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition text-gray-900 placeholder-gray-400"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <div className="flex items-center justify-between text-sm">
            <label className="flex items-center">
              <input type="checkbox" className="mr-2 rounded" />
              <span className="text-gray-600">Remember me</span>
            </label>
            <a href="/forgot-password" className="text-blue-600 hover:text-blue-800 font-semibold">
              Forgot password?
            </a>
          </div>

          <button 
            type="submit" 
            disabled={isLoading}
            className="bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 transition font-semibold disabled:bg-gray-400 disabled:cursor-not-allowed mt-2"
          >
            {isLoading ? 'Signing In...' : 'Sign In'}
          </button>
        </form>

        {message && (
          <div className={`mt-4 p-3 rounded-lg text-center text-sm ${
            message.includes('✅') ? 'bg-green-50 text-green-700' : 
            message.includes('❌') ? 'bg-red-50 text-red-700' : 
            'bg-blue-50 text-blue-700'
          }`}>
            {message}
          </div>
        )}

        <div className="mt-6 text-center">
          <p className="text-sm text-gray-600">
            Don't have an account?{' '}
            <a href="/register" className="text-blue-600 hover:text-blue-800 font-semibold">
              Create Account
            </a>
          </p>
        </div>
      </div>
    </main>
  );
}
