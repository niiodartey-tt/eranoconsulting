import React, { useEffect } from 'react';
import { useRouter } from 'next/router';
import { useAuthStore } from '../lib/auth';

interface ProtectedRouteProps {
  children: React.ReactNode;
  allowedRoles?: string[];
  fallbackPath?: string;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  allowedRoles = [],
  fallbackPath = '/login',
}) => {
  const router = useRouter();
  const { isAuthenticated, user, isLoading } = useAuthStore();
  
  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.replace(`${fallbackPath}?redirect=${encodeURIComponent(router.asPath)}`);
    }
    
    if (!isLoading && isAuthenticated && allowedRoles.length > 0 && user) {
      if (!allowedRoles.includes(user.role)) {
        router.replace('/unauthorized');
      }
    }
  }, [isAuthenticated, user, isLoading, router, allowedRoles, fallbackPath]);
  
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }
  
  if (!isAuthenticated || (allowedRoles.length > 0 && !allowedRoles.includes(user?.role || ''))) {
    return null;
  }
  
  return <>{children}</>;
};
