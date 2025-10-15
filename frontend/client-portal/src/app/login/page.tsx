'use client'
import { useState } from 'react'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({ username: email, password }),
      })

      const text = await res.text()
      let data

      try {
        data = JSON.parse(text)
      } catch {
        throw new Error(`Invalid JSON: ${text}`)
      }

      if (!res.ok) {
        throw new Error(data?.detail || 'Login failed')
      }

      console.log('Login response:', data)

      // Save tokens
      localStorage.setItem('access_token', data.access_token)
      localStorage.setItem('refresh_token', data.refresh_token)

      // Redirect
      window.location.href = '/dashboard'
    } catch (err: any) {
      console.error('Login error:', err)
      setError(err.message)
    } finally {
      setLoading(false)
    }
  } // ✅ <-- this closing brace was missing

  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-gray-50 p-6">
      <div className="w-full max-w-sm bg-white shadow-md rounded-xl p-8">
        <h1 className="text-2xl font-semibold text-center text-blue-700 mb-6">
          Erano Client Portal
        </h1>

        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="mt-1 w-full p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="mt-1 w-full p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400"
              required
            />
          </div>

          {error && <p className="text-red-600 text-sm">{error}</p>}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white p-2 rounded-md hover:bg-blue-700 transition"
          >
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>
      </div>
    </main>
  )
}
