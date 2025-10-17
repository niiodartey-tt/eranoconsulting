'use client';

import ClientDashboardGuard from './components/ClientDashboardGuard';

export default function ClientDashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <ClientDashboardGuard>
      {children}
    </ClientDashboardGuard>
  );
}