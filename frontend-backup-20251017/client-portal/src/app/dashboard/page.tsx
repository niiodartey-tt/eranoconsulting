"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";


export default function Dashboard() {
  const router = useRouter();

  const handleLogout = () => {
    // Remove token
    localStorage.removeItem("access_token");

    // Optionally clear refresh token, etc.
    // localStorage.removeItem("refresh_token");

    // Redirect to login
    router.push("/login");
  };

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      router.push("/login");
    }
  }, [router]);


  return (
    <div className="flex flex-col items-center justify-center min-h-screen gap-4">
      <h1 className="text-2xl font-semibold">Welcome to your Dashboard</h1>
      <p>You are successfully logged in ✅</p>

      <button
        onClick={handleLogout}
        className="px-4 py-2 text-white bg-red-600 rounded-md hover:bg-red-700 transition"
      >
        Logout
      </button>
    </div>
  );
}
