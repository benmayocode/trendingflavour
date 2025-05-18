import { Card } from "react-bootstrap";

export default function SentimentTrendCard() {
  return (
    <Card className="mb-4 shadow-sm">
      <Card.Body>
        <Card.Title>📘 Sentiment Trend</Card.Title>
        <Card.Text>
          <strong>Sentiment Trend</strong> measures how user sentiment for a category is changing over time,
          using linear regression on weekly average sentiment scores.
        </Card.Text>

        <Card.Subtitle className="mt-3 mb-2 text-muted">🔎 How it works</Card.Subtitle>
        <ul>
          <li>Group reviews by <strong>week</strong> for each category</li>
          <li>Calculate <strong>average sentiment</strong> per week</li>
          <li>Run linear regression: <code>REGR_SLOPE(avg_sentiment, week_num)</code></li>
          <li>Return the slope as the trend indicator</li>
        </ul>

        <Card.Subtitle className="mt-3 mb-2 `text-muted">📈 Interpretation</Card.Subtitle>
        <ul>
          <li><strong>Positive slope</strong> → improving sentiment</li>
          <li><strong>Negative slope</strong> → declining sentiment</li>
          <li>Only categories with ≥3 weeks of data are included</li>
        </ul>
      </Card.Body>
    </Card>
  );
}
