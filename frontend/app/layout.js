// src/app/layout.js
import 'bootstrap/dist/css/bootstrap.min.css';
import 'leaflet/dist/leaflet.css';

export const metadata = {
  title: 'TrendingFlavours',
  description: 'Discover trending foods in your area',
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
