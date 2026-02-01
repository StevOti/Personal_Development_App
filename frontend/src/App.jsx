import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { HabitsPage } from './pages/HabitsPage';
import { CreateHabitPage } from './pages/CreateHabitPage';
import { HabitDetailPage } from './pages/HabitDetailPage';
import './index.css';

function App() {
  return (
    <Router>
      <AuthProvider>
        <Routes>
          {/* Public Routes */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />

          {/* Protected Routes */}
          <Route
            path="/habits"
            element={
              <ProtectedRoute>
                <HabitsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/habits/create"
            element={
              <ProtectedRoute>
                <CreateHabitPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/habits/:id"
            element={
              <ProtectedRoute>
                <HabitDetailPage />
              </ProtectedRoute>
            }
          />

          {/* Catch-all */}
          <Route path="/" element={<Navigate to="/habits" replace />} />
          <Route path="*" element={<Navigate to="/habits" replace />} />
        </Routes>
      </AuthProvider>
    </Router>
  );
}

export default App;
