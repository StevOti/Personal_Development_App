import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { analyticsAPI } from '../services/api';
import { Doughnut } from 'react-chartjs-2';
import '../styles/AnalyticsPreview.css';

export function AnalyticsPreviewCard() {
  const [overview, setOverview] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      const response = await analyticsAPI.overview();
      setOverview(response.data);
      setError(null);
    } catch (err) {
      console.error('Failed to fetch analytics preview:', err);
      setError('Failed to load analytics');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="analytics-preview-card">
        <h2>📊 Quick Stats</h2>
        <div className="loading-skeleton">Loading...</div>
      </div>
    );
  }

  if (error || !overview) {
    return null;
  }

  // Category breakdown chart
  const categoryColors = {
    health: '#ff6384',
    productivity: '#36a2eb',
    finance: '#ffce56',
    learning: '#4bc0c0',
    relationships: '#9966ff',
    other: '#ff9f40',
  };

  const chartData = {
    labels: overview?.category_breakdown.map((c) => c.category_label) || [],
    datasets: [
      {
        data: overview?.category_breakdown.map((c) => c.total_completions) || [],
        backgroundColor: overview?.category_breakdown.map(
          (c) => categoryColors[c.category] || '#ccc'
        ) || [],
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom',
      },
    },
  };

  return (
    <div className="analytics-preview-card">
      <div className="card-header">
        <h2>📊 Quick Stats</h2>
        <Link to="/analytics" className="view-details-link">
          View Full Dashboard →
        </Link>
      </div>

      <div className="quick-stats">
        <div className="stat-item">
          <span className="stat-label">Total Habits</span>
          <span className="stat-number">{overview.total_habits}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Completion Rate</span>
          <span className="stat-number">{overview.completion_rate}%</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Current Streak</span>
          <span className="stat-number">🔥 {overview.current_streak}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Total Logged</span>
          <span className="stat-number">{overview.total_completions}</span>
        </div>
      </div>

      {overview.category_breakdown.length > 0 && (
        <div className="chart-preview">
          <h3>Category Distribution</h3>
          <div className="chart-container-small">
            <Doughnut data={chartData} options={chartOptions} />
          </div>
        </div>
      )}
    </div>
  );
}
