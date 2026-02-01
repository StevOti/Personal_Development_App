import { useLocation } from 'react-router-dom';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import '../styles/Navigation.css';

export function Navigation() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  // Don't show navbar on login/register pages
  const hideNavbar = ['/login', '/register'].includes(location.pathname);

  const handleLogout = async () => {
    try {
      await logout();
      navigate('/login');
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  if (!user || hideNavbar) return null;

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-logo">
          🎯 HabitTracker
        </Link>

        <div className="nav-menu">
          <Link to="/habits" className="nav-link">
            Habits
          </Link>
          <Link to="/analytics" className="nav-link">
            📊 Analytics
          </Link>
        </div>

        <div className="nav-user">
          <span className="user-info">👤 {user.username}</span>
          <button onClick={handleLogout} className="btn-logout">
            Logout
          </button>
        </div>
      </div>
    </nav>
  );
}
