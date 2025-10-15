'use client'
import { useEffect, useState } from 'react'

export default function Dashboard() {
  const [token, setToken] = useState<string | null>(null)
  const [isMounted, setIsMounted] = useState(false)

  useEffect(() => {
    setIsMounted(true) // ✅ ensures client-only render after hydration
    const t = localStorage.getItem('access_token')
    if (!t) {
      window.location.href = '/login'
    } else {
      setToken(t)
    }
  }, [])

  // 🧠 wait until client is mounted
  if (!isMounted) return null

  if (!token) return <p>Loading...</p>

  return (
    <main className="p-8">
      <h1 className="text-2xl font-bold text-blue-700">
        Welcome to Erano Consulting Dashboard
      </h1>
      <p className="mt-2 text-gray-600">You are successfully logged in ✅</p>
    </main>
  )
}
