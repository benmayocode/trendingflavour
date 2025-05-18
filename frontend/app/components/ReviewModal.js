'use client';
import { useEffect, useState } from 'react';
import { Modal, Button, Spinner } from 'react-bootstrap';

export default function ReviewModal({ show, onHide, category }) {
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!category || !show) return;
    setLoading(true);
    fetch(`http://127.0.0.1:8000/api/reviews/by_category?category=${category}`)
      .then(res => res.json())
      .then(data => setReviews(data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [category, show]);

  return (
    <Modal show={show} onHide={onHide} size="lg">
      <Modal.Header closeButton>
        <Modal.Title>Reviews for {category}</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        {loading ? (
          <Spinner animation="border" />
        ) : reviews.length === 0 ? (
          <p>No reviews found.</p>
        ) : (
          <ul className="list-group">
            {reviews.map((r) => (
              <li key={r.review_id} className="list-group-item">
                <strong>{r.title || 'Untitled'} ({r.rating}★)</strong><br />
                <small>{r.published_date?.split('T')[0]}</small><br />
                <span className={`badge bg-${r.sentiment_label === 'positive' ? 'success' : r.sentiment_label === 'negative' ? 'danger' : 'secondary'}`}>
                  {r.sentiment_label}
                </span>
                <p className="mt-1">{r.body}</p>
              </li>
            ))}
          </ul>
        )}
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={onHide}>Close</Button>
      </Modal.Footer>
    </Modal>
  );
}
