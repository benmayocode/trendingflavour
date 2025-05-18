import { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png';
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';

// Fix Leaflet's broken default icon paths
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x.src,
  iconUrl: markerIcon.src,
  shadowUrl: markerShadow.src,
});

const DEFAULT_POSITION = [51.52, -0.08];

// components/MapView.js
export default function MapView({ selectedCategory }) {
  console.log('MapView rendered with selectedCategory:', selectedCategory);
  const [locations, setLocations] = useState([]);

  useEffect(() => {
    fetch('http://127.0.0.1:8000/api/locations')
      .then(res => res.json())
      .then(setLocations)
      .catch(err => console.error('Error fetching locations:', err));
  }, []);

  const filtered = selectedCategory
    ? locations.filter(loc => loc.category === selectedCategory)
    : locations;

  return (
    <MapContainer center={[51.52, -0.08]} zoom={15} style={{ height: '500px', width: '100%' }}>
      <TileLayer
        attribution='&copy; OpenStreetMap contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      {filtered.map(loc => (
        <Marker key={loc.location_id} position={[loc.latitude, loc.longitude]}>
          <Popup>
            <strong>{loc.name}</strong><br />
            {loc.category}
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  );
}
