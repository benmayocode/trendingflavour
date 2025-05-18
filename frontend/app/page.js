'use client';
import dynamic from 'next/dynamic';
import { useEffect, useState } from 'react';
import { Button } from 'react-bootstrap';
import { Spinner, Alert, Accordion, Row, Col } from 'react-bootstrap';
import SentimentTrendChart from './components/SentimentTrendChart';
import TrendingCategoriesTable from './components/TrendingCategoriesTable';
import SentimentTrendCard from './components/SentimentTrendDefinition';
import ReviewModal from './components/ReviewModal';
const MapView = dynamic(() => import('./components/MapView'), { ssr: false });

export default function HomePage() {
  const [locations, setLocations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [modalOpen, setModalOpen] = useState(false);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/api/locations")
      .then(res => res.json())
      .then(data => setLocations(data))
      .catch(err => console.error("Error loading locations", err))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="p-4">
      <div className="d-flex align-items-center justify-content-between mb-3">
        <h3 className="mb-0">Identifying Food Trends</h3>
        {selectedCategory && (
          <Button variant="primary" onClick={() => setModalOpen(true)}>
            View Reviews
          </Button>
        )}
      </div>

      {loading && <Spinner animation="border" />}
      {!loading && locations.length === 0 && (
        <Alert variant="info">No locations found.</Alert>
      )}

      {!loading && locations.length > 0 && (
        <Row className="my-4">
          <Col md={6}>
            <MapView locations={locations} selectedCategory={selectedCategory} />
          </Col>
          <Col md={6}>
            <TrendingCategoriesTable
              selectedCategory={selectedCategory}
              setSelectedCategory={setSelectedCategory}
            />
          </Col>
        </Row>
      )}

      <ReviewModal show={modalOpen} onHide={() => setModalOpen(false)} category={selectedCategory} />
      <Accordion>
        <Accordion.Item eventKey="0">
          <Accordion.Header>What is Sentiment Trend?</Accordion.Header>
          <Accordion.Body>
            <SentimentTrendCard />
          </Accordion.Body>
        </Accordion.Item>
      </Accordion>
      <div className="my-4">
        <SentimentTrendChart selectedCategory={selectedCategory} />
      </div>

    </div>
  );
}
