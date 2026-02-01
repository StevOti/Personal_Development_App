import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { habitAPI } from '../services/api';
import '../styles/Habits.css';

export function HabitsPage() {
  const [habits, setHabits] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);

  useEffect(() => {
    fetchHabits();
  }, [page]);

  const fetchHabits = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await habitAPI.list(page);
      setHabits(response.data.results);
    } catch (err) {
      setError('Failed to load habits');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this habit?')) {
      try {
        await habitAPI.delete(id);
        setHabits(habits.filter((h) => h.id !== id));
      } catch (err) {
        setError('Failed to delete habit');
      }
    }
  };

  const getCategoryColor = (category) => {
    const colors = {
      health: '#ff6b6b',
      productivity: '#4ecdc4',
      finance: '#45b7d1',
      learning: '#96ceb4',
      relationships: '#ffeaa7',
      other: '#dfe6e9',
    };
    return colors[category] || '#dfe6e9';
  };

  if (loading) return <div className="loading">Loading habits...</div>;

  return (
    <div className="habits-container">
      <div className="habits-header">
        <h1>My Habits</h1>
        <Link to="/habits/create" className="btn btn-primary">
          Create Habit
        </Link>
      </div>

      {error && <div className="error-message">{error}</div>}

      {habits.length === 0 ? (
        <div className="empty-state">
          <p>No habits yet. Start by creating one!</p>
          <Link to="/habits/create" className="btn btn-primary">
            Create Your First Habit
          </Link>
        </div>
      ) : (
        <div className="habits-grid">
          {habits.map((habit) => (
            <div key={habit.id} className="habit-card">
              <div
                className="habit-category"
                style={{ backgroundColor: getCategoryColor(habit.category) }}
              >
                {habit.category.toUpperCase()}
              </div>

              <h3>{habit.name}</h3>

              <div className="habit-stats">
                <div className="stat">
                  <span className="stat-label">Current Streak</span>
                  <span className="stat-value">{habit.current_streak} 🔥</span>
                </div>
                <div className="stat">
                  <span className="stat-label">Frequency</span>
                  <span className="stat-value">{habit.frequency}</span>
                </div>
              </div>

              <div className="habit-actions">
                <Link
                  to={`/habits/${habit.id}`}
                  className="btn btn-secondary btn-small"
                >
                  View
                </Link>
                <button
                  onClick={() => handleDelete(habit.id)}
                  className="btn btn-danger btn-small"
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
