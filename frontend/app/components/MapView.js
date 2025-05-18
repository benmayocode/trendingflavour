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

export default function MapView() {
  const [locations, setLocations] = useState([]);

  useEffect(() => {
    fetch('http://127.0.0.1:8000/api/locations')
      .then(res => res.json())
      .then(setLocations)
      .catch(console.error);
  }, []);

  return (
    <MapContainer center={DEFAULT_POSITION} zoom={15} style={{ height: '500px', width: '100%' }}>
      <TileLayer
        attribution='&copy; OpenStreetMap contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      {locations.map(loc => (
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
