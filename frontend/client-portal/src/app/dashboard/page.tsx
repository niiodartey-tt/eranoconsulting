'use client'

import ProtectedRoute from '@/components/ProtectedRoute'

export default function DashboardPage() {
  return (
    <ProtectedRoute>
      <main className="p-8">
        <h1 className="text-2xl font-bold text-blue-700">
          Welcome to your Dashboard
        </h1>
        <p className="mt-2 text-gray-600">
          You are successfully logged in ✅
        </p>
      </main>
    </ProtectedRoute>
  )
}
