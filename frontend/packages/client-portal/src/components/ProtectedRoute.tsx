'use client'
import { useState, useEffect } from 'react'

interface ProtectedRouteProps {
  children: React.ReactNode
}

export default function ProtectedRoute({ children }: ProtectedRouteProps) {
  const [isMounted, setIsMounted] = useState(false)
  const [token, setToken] = useState<string | null>(null)

  useEffect(() => {
    setIsMounted(true)
    const t = localStorage.getItem('access_token')
    if (!t) {
      window.location.href = '/login'
    } else {
      setToken(t)
    }
  }, [])

  if (!isMounted) return null
  if (!token) return <p>Loading...</p>

  return <>{children}</>
}
