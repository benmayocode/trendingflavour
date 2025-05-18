'use client';

import { useEffect, useState } from 'react';
import { Line } from 'react-chartjs-2';
import {
    Chart as ChartJS,
    LineElement,
    CategoryScale,
    LinearScale,
    PointElement,
    Legend,
    Tooltip
} from 'chart.js';

ChartJS.register(LineElement, CategoryScale, LinearScale, PointElement, Legend, Tooltip);

export default function SentimentTrendChart({ selectedCategory }) {
    const [chartData, setChartData] = useState(null);

    const COLOURS = [
        '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0',
        '#9966FF', '#FF9F40', '#66D36E', '#C9CBCF',
        '#B94D8C', '#3E95CD', '#8E5EA2', '#3CBA9F'
    ];


    useEffect(() => {
        async function fetchData() {
            try {
                const res = await fetch('http://127.0.0.1:8000/api/trends/sentiment_over_time');
                const data = await res.json();

                // Group by category
                const grouped = {};
                data.forEach(({ category, date, avg_sentiment }) => {
                    if (!grouped[category]) grouped[category] = {};
                    grouped[category][date] = avg_sentiment;
                });

                // Get all unique sorted dates
                const dates = Array.from(
                    new Set(data.map(row => row.date))
                ).sort();

                // Filter categories
                const filtered = selectedCategory
                    ? { [selectedCategory]: grouped[selectedCategory] }
                    : grouped;

                const datasets = Object.entries(filtered).map(([category, values], index) => ({
                    label: category,
                    data: dates.map(date => values?.[date] ?? null),
                    tension: 0.3,
                    spanGaps: true,
                    borderColor: COLOURS[index % COLOURS.length],
                    backgroundColor: COLOURS[index % COLOURS.length],
                }));
                setChartData({
                    labels: dates,
                    datasets
                });
            } catch (err) {
                console.error('Failed to load sentiment data:', err);
            }
        }

        fetchData();
    }, [selectedCategory]);

    if (!chartData) return <p>Loading chart…</p>;

    return (
<div className="mt-4" style={{ height: '400px' }}>
  <Line
    data={chartData}
    options={{
      maintainAspectRatio: false,
      responsive: true,
      plugins: {
        legend: { position: 'bottom' }
      }
    }}
  />
</div>
    );
}
