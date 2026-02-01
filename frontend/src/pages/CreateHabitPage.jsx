import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { habitAPI } from '../services/api';
import '../styles/Habits.css';

export function CreateHabitPage() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    category: 'health',
    frequency: 'daily',
    goal_count: 1,
    start_date: new Date().toISOString().split('T')[0],
  });

  const categories = [
    'health',
    'productivity',
    'finance',
    'learning',
    'relationships',
    'other',
  ];
  const frequencies = ['daily', 'weekly', 'monthly'];

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: name === 'goal_count' ? parseInt(value) : value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      await habitAPI.create(formData);
      navigate('/habits');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create habit');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="create-habit-container">
      <h1>Create New Habit</h1>

      {error && <div className="error-message">{error}</div>}

      <form onSubmit={handleSubmit} className="habit-form">
        <div className="form-group">
          <label htmlFor="name">Habit Name *</label>
          <input
            id="name"
            name="name"
            type="text"
            value={formData.name}
            onChange={handleChange}
            placeholder="e.g., Morning Workout"
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="description">Description</label>
          <textarea
            id="description"
            name="description"
            value={formData.description}
            onChange={handleChange}
            placeholder="What is this habit about?"
            rows="4"
          />
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="category">Category *</label>
            <select
              id="category"
              name="category"
              value={formData.category}
              onChange={handleChange}
              required
            >
              {categories.map((cat) => (
                <option key={cat} value={cat}>
                  {cat.charAt(0).toUpperCase() + cat.slice(1)}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="frequency">Frequency *</label>
            <select
              id="frequency"
              name="frequency"
              value={formData.frequency}
              onChange={handleChange}
              required
            >
              {frequencies.map((freq) => (
                <option key={freq} value={freq}>
                  {freq.charAt(0).toUpperCase() + freq.slice(1)}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="goal_count">Goal Count (per period) *</label>
            <input
              id="goal_count"
              name="goal_count"
              type="number"
              min="1"
              value={formData.goal_count}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="start_date">Start Date *</label>
            <input
              id="start_date"
              name="start_date"
              type="date"
              value={formData.start_date}
              onChange={handleChange}
              required
            />
          </div>
        </div>

        <div className="form-actions">
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? 'Creating...' : 'Create Habit'}
          </button>
          <button
            type="button"
            className="btn btn-secondary"
            onClick={() => navigate('/habits')}
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}
