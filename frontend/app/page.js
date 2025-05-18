// src/app/page.js
'use client';

import { useEffect, useState } from 'react';
import { Spinner, Alert } from 'react-bootstrap';

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
    <div className="container mt-4">
      <h1>📍 TrendingFlavours</h1>
      {loading && <Spinner animation="border" />}
      {!loading && locations.length === 0 && (
        <Alert variant="info">No locations found.</Alert>
      )}
      {!loading && locations.length > 0 && (
        <ul className="list-group">
          {locations.map((loc) => (
            <li key={loc.location_id} className="list-group-item">
              {loc.name} — <small>{loc.category}</small>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
