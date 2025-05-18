// src/app/page.js
'use client';
import dynamic from 'next/dynamic';

import { useEffect, useState } from 'react';
import { Spinner, Alert } from 'react-bootstrap';
const MapView = dynamic(() => import('./components/MapView'), {
  ssr: false,
});

export default function HomePage() {
  const [locations, setLocations] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/api/locations")
      .then(res => res.json())
      .then(data => setLocations(data))
      .catch(err => console.error("Error loading locations", err))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="p-4">
      <h3>Trending Food Spots</h3>
      {loading && <Spinner animation="border" />}
      {!loading && locations.length === 0 && <Alert variant="info">No locations found.</Alert>}
      {!loading && locations.length > 0 && <MapView locations={locations} />}
    </div>
  );
}
