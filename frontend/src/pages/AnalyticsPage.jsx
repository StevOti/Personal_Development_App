import { useState, useEffect } from 'react';
import { analyticsAPI } from '../services/api';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Line, Bar, Doughnut } from 'react-chartjs-2';
import '../styles/Analytics.css';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

const AnalyticsPage = () => {
  const [overview, setOverview] = useState(null);
  const [weeklyData, setWeeklyData] = useState(null);
  const [monthlyData, setMonthlyData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      setError(null);

      const [overviewRes, weeklyRes, monthlyRes] = await Promise.all([
        analyticsAPI.overview(),
        analyticsAPI.weekly(),
        analyticsAPI.monthly(),
      ]);

      setOverview(overviewRes.data);
      setWeeklyData(weeklyRes.data);
      setMonthlyData(monthlyRes.data);
    } catch (err) {
      console.error('Failed to fetch analytics:', err);
      setError('Failed to load analytics data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="analytics-container">
        <div className="loading">Loading analytics...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="analytics-container">
        <div className="error-message">{error}</div>
        <button onClick={fetchAnalytics} className="btn-primary">
          Retry
        </button>
      </div>
    );
  }

  // Weekly chart data
  const weeklyChartData = {
    labels: weeklyData?.daily_data.map((d) => {
      const date = new Date(d.date);
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    }).reverse() || [],
    datasets: [
      {
        label: 'Completion Rate (%)',
        data: weeklyData?.daily_data.map((d) => d.completion_rate).reverse() || [],
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        tension: 0.3,
      },
      {
        label: 'Completions',
        data: weeklyData?.daily_data.map((d) => d.completions).reverse() || [],
        borderColor: 'rgb(153, 102, 255)',
        backgroundColor: 'rgba(153, 102, 255, 0.2)',
        tension: 0.3,
      },
    ],
  };

  // Category breakdown chart data
  const categoryColors = {
    health: '#ff6384',
    productivity: '#36a2eb',
    finance: '#ffce56',
    learning: '#4bc0c0',
    relationships: '#9966ff',
    other: '#ff9f40',
  };

  const categoryChartData = {
    labels: overview?.category_breakdown.map((c) => c.category_label) || [],
    datasets: [
      {
        label: 'Completions',
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
        position: 'top',
      },
    },
  };

  return (
    <div className="analytics-container">
      <div className="analytics-header">
        <h1>Analytics Dashboard</h1>
        <button onClick={fetchAnalytics} className="btn-secondary">
          Refresh
        </button>
      </div>

      {/* Overview Cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">📊</div>
          <div className="stat-content">
            <h3>Total Habits</h3>
            <p className="stat-value">{overview?.total_habits || 0}</p>
            <span className="stat-label">
              {overview?.active_habits || 0} active
            </span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">✅</div>
          <div className="stat-content">
            <h3>Completion Rate</h3>
            <p className="stat-value">{overview?.completion_rate || 0}%</p>
            <span className="stat-label">Last 30 days</span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">🔥</div>
          <div className="stat-content">
            <h3>Current Streak</h3>
            <p className="stat-value">{overview?.current_streak || 0}</p>
            <span className="stat-label">days</span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">🏆</div>
          <div className="stat-content">
            <h3>Longest Streak</h3>
            <p className="stat-value">{overview?.longest_streak || 0}</p>
            <span className="stat-label">days</span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">📈</div>
          <div className="stat-content">
            <h3>Total Completions</h3>
            <p className="stat-value">{overview?.total_completions || 0}</p>
            <span className="stat-label">all time</span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">📅</div>
          <div className="stat-content">
            <h3>This Month</h3>
            <p className="stat-value">{monthlyData?.total_completions || 0}</p>
            <span className="stat-label">completions</span>
          </div>
        </div>
      </div>

      {/* Charts Section */}
      <div className="charts-grid">
        <div className="chart-card">
          <h2>Weekly Progress</h2>
          <div className="chart-container">
            <Line data={weeklyChartData} options={chartOptions} />
          </div>
        </div>

        <div className="chart-card">
          <h2>Category Breakdown</h2>
          <div className="chart-container">
            {overview?.category_breakdown.length > 0 ? (
              <Doughnut data={categoryChartData} options={chartOptions} />
            ) : (
              <p className="no-data">No category data available</p>
            )}
          </div>
        </div>
      </div>

      {/* Category Details */}
      {overview?.category_breakdown.length > 0 && (
        <div className="category-details">
          <h2>Category Statistics</h2>
          <div className="category-list">
            {overview.category_breakdown.map((cat) => (
              <div key={cat.category} className="category-item">
                <div
                  className="category-color"
                  style={{
                    backgroundColor: categoryColors[cat.category] || '#ccc',
                  }}
                ></div>
                <div className="category-info">
                  <h3>{cat.category_label}</h3>
                  <p>
                    {cat.habit_count} habit{cat.habit_count !== 1 ? 's' : ''} •{' '}
                    {cat.total_completions} completion
                    {cat.total_completions !== 1 ? 's' : ''}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Monthly Summary */}
      <div className="monthly-summary">
        <h2>
          {new Date(monthlyData?.year, monthlyData?.month - 1).toLocaleDateString(
            'en-US',
            { month: 'long', year: 'numeric' }
          )}
        </h2>
        <div className="summary-stats">
          <div className="summary-item">
            <span className="summary-label">Completions:</span>
            <span className="summary-value">{monthlyData?.total_completions}</span>
          </div>
          <div className="summary-item">
            <span className="summary-label">Completion Rate:</span>
            <span className="summary-value">{monthlyData?.completion_rate}%</span>
          </div>
          <div className="summary-item">
            <span className="summary-label">Active Habits:</span>
            <span className="summary-value">{monthlyData?.total_habits}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalyticsPage;
