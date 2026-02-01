import axios from 'axios';

// Create axios instance with base URL pointing to Django backend
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add JWT token to requests if available
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Handle token refresh on 401
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/auth/refresh/`, {
            refresh: refreshToken,
          });

          const { access } = response.data;
          localStorage.setItem('access_token', access);
          originalRequest.headers.Authorization = `Bearer ${access}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        // Refresh failed, clear tokens and redirect to login
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
      }
    }

    return Promise.reject(error);
  }
);

// Authentication endpoints
export const authAPI = {
  register: (username, email, password, password2) =>
    api.post('/auth/signup/', { username, email, password, password2 }),
  login: (username, password) =>
    api.post('/auth/login/', { username, password }),
  logout: (refresh) => api.post('/auth/logout/', { refresh }),
  profile: () => api.get('/auth/profile/'),
};

// Habit endpoints
export const habitAPI = {
  list: (page = 1) => api.get(`/habits/?page=${page}`),
  create: (habitData) => api.post('/habits/', habitData),
  retrieve: (id) => api.get(`/habits/${id}/`),
  update: (id, habitData) => api.patch(`/habits/${id}/`, habitData),
  delete: (id) => api.delete(`/habits/${id}/`),
  log: (id, logData) => api.post(`/habits/${id}/log/`, logData),
  stats: (id) => api.get(`/habits/${id}/stats/`),
};

// Analytics endpoints
export const analyticsAPI = {
  overview: () => api.get('/habits/analytics/overview/'),
  weekly: () => api.get('/habits/analytics/weekly/'),
  monthly: () => api.get('/habits/analytics/monthly/'),
};

export default api;
