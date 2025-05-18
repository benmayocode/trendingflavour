// app/components/TrendingCategoriesTable.js
'use client';

import { useEffect, useState } from 'react';
import { Table, Spinner, Alert } from 'react-bootstrap';

export default function TrendingCategoriesTable({ selectedCategory, setSelectedCategory }) {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetch("http://127.0.0.1:8000/api/trends_cosmos/trending_categories")
      .then(res => {
        if (!res.ok) throw new Error("Failed to fetch trending categories");
        return res.json();
      })
      .then(setCategories)
      .catch(err => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <Spinner animation="border" />;
  if (error) return <Alert variant="danger">{error}</Alert>;

  return (
    <div className="mt-4">
      <h4>📈 Trending Categories</h4>
      <Table striped bordered hover>
        <thead>
          <tr>
            <th>Category</th>
            <th>Trend Slope</th>
            <th>Weeks Count</th>
          </tr>
        </thead>
        <tbody>
          {categories.map((row) => (
          <tr
          key={row.category}
          className={row.category === selectedCategory ? 'table-primary' : ''}
          style={{ cursor: 'pointer' }}
          onClick={() => setSelectedCategory(row.category === selectedCategory ? null : row.category)}
        >
            <td>{row.category}</td>
              <td className={row.sentiment_trend_slope > 0 ? 'text-success' : 'text-danger'}>
                {row.sentiment_trend_slope.toFixed(3)}
              </td>
              <td>{row.weeks_count}</td>
            </tr>
          ))}
        </tbody>
      </Table>
    </div>
  );
}
