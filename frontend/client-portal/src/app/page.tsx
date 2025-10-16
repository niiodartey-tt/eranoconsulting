'use client';

import { useEffect, useState } from 'react';

export default function Home() {
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/`)
      .then((res) => res.json())
      .then((data) => setData(data))
      .catch((err) => console.error('Error fetching:', err));
  }, []);

  return (
    <main style={{ padding: 40 }}>
      <h1>Client Portal Dashboard</h1>
      <p>Welcome to Eranos Consulting.</p>

      {data ? (
        <pre>{JSON.stringify(data, null, 2)}</pre>
      ) : (
        <p>Loading data from backend...</p>
      )}
    </main>
  );
}
