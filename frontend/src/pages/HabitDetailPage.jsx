import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { habitAPI } from '../services/api';
import '../styles/Habits.css';

export function HabitDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [habit, setHabit] = useState(null);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showLogForm, setShowLogForm] = useState(false);
  const [logDate, setLogDate] = useState(new Date().toISOString().split('T')[0]);
  const [logNotes, setLogNotes] = useState('');
  const [loggingLoading, setLoggingLoading] = useState(false);

  useEffect(() => {
    fetchHabitDetails();
  }, [id]);

  const fetchHabitDetails = async () => {
    setLoading(true);
    setError(null);
    try {
      const [habitRes, statsRes] = await Promise.all([
        habitAPI.retrieve(id),
        habitAPI.stats(id),
      ]);
      setHabit(habitRes.data);
      setStats(statsRes.data);
    } catch (err) {
      setError('Failed to load habit details');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleLogCompletion = async (e) => {
    e.preventDefault();
    setLoggingLoading(true);
    try {
      await habitAPI.log(id, {
        log_date: logDate,
        notes: logNotes,
      });
      setLogDate(new Date().toISOString().split('T')[0]);
      setLogNotes('');
      setShowLogForm(false);
      fetchHabitDetails(); // Refresh to see updated stats
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to log completion');
    } finally {
      setLoggingLoading(false);
    }
  };

  const handleDelete = async () => {
    if (window.confirm('Are you sure? This cannot be undone.')) {
      try {
        await habitAPI.delete(id);
        navigate('/habits');
      } catch (err) {
        setError('Failed to delete habit');
      }
    }
  };

  if (loading) return <div className="loading">Loading habit details...</div>;
  if (!habit) return <div className="error-message">Habit not found</div>;

  return (
    <div className="habit-detail-container">
      <button className="btn-back" onClick={() => navigate('/habits')}>
        ← Back to Habits
      </button>

      {error && <div className="error-message">{error}</div>}

      <div className="habit-detail-header">
        <h1>{habit.name}</h1>
        <div className="category-badge" style={{ backgroundColor: '#4ecdc4' }}>
          {habit.category.toUpperCase()}
        </div>
      </div>

      {habit.description && (
        <p className="habit-description">{habit.description}</p>
      )}

      <div className="habit-details-grid">
        <div className="detail-card">
          <h3>Statistics</h3>
          {stats && (
            <div className="stats-display">
              <div className="stat-item">
                <span className="stat-label">Current Streak</span>
                <span className="stat-number">{stats.current_streak}</span>
                <span className="stat-unit">days 🔥</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Longest Streak</span>
                <span className="stat-number">{stats.longest_streak}</span>
                <span className="stat-unit">days</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Total Completions</span>
                <span className="stat-number">{stats.total_completions}</span>
                <span className="stat-unit">times</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Completion Rate</span>
                <span className="stat-number">
                  {(stats.completion_rate * 100).toFixed(1)}%
                </span>
              </div>
            </div>
          )}
        </div>

        <div className="detail-card">
          <h3>Information</h3>
          <div className="info-display">
            <div className="info-item">
              <span className="info-label">Frequency:</span>
              <span className="info-value">
                {habit.frequency.charAt(0).toUpperCase() + habit.frequency.slice(1)}
              </span>
            </div>
            <div className="info-item">
              <span className="info-label">Goal:</span>
              <span className="info-value">{habit.goal_count} times per period</span>
            </div>
            <div className="info-item">
              <span className="info-label">Start Date:</span>
              <span className="info-value">
                {new Date(habit.start_date).toLocaleDateString()}
              </span>
            </div>
            <div className="info-item">
              <span className="info-label">Created:</span>
              <span className="info-value">
                {new Date(habit.created_at).toLocaleDateString()}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div className="log-section">
        <h2>Log Completion</h2>
        {showLogForm ? (
          <form onSubmit={handleLogCompletion} className="log-form">
            <div className="form-group">
              <label htmlFor="log_date">Date</label>
              <input
                id="log_date"
                type="date"
                value={logDate}
                onChange={(e) => setLogDate(e.target.value)}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="log_notes">Notes (optional)</label>
              <textarea
                id="log_notes"
                value={logNotes}
                onChange={(e) => setLogNotes(e.target.value)}
                placeholder="How did it go?"
                rows="3"
              />
            </div>

            <div className="form-actions">
              <button
                type="submit"
                className="btn btn-primary"
                disabled={loggingLoading}
              >
                {loggingLoading ? 'Logging...' : 'Log Completion'}
              </button>
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => setShowLogForm(false)}
              >
                Cancel
              </button>
            </div>
          </form>
        ) : (
          <button
            className="btn btn-primary btn-large"
            onClick={() => setShowLogForm(true)}
          >
            + Log Today
          </button>
        )}
      </div>

      <div className="detail-actions">
        <button className="btn btn-danger" onClick={handleDelete}>
          Delete Habit
        </button>
      </div>
    </div>
  );
}
