import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  console.log('🔍 Token:', token);
  console.log('🔍 URL:', config.url);
  
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
    console.log('✅ Auth header:', config.headers.Authorization);
  } else {
    console.log('❌ No token!');
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.log('❌ Error response:', error.response?.status);
    console.log('❌ Error config:', error.config?.url);
    return Promise.reject(error);
  }
);


// AUTH ENDPOINTS
export const authAPI = {
  login: (credentials) => api.post('/auth/login', credentials),
  register: (userData) => api.post('/auth/register', userData),
  getCurrentUser: () => api.get('/auth/me'),
  changePassword: (passwords) => api.post('/auth/change-password', passwords),
};

// INVENTORY ENDPOINTS
export const inventoryAPI = {
  getAll: (category) => api.get('/inventory/', { params: { category } }),
  getById: (id) => api.get(`/inventory/${id}/`),
  create: (itemData) => api.post('/inventory/', itemData),
  update: (id, itemData) => api.put(`/inventory/${id}/`, itemData),
  delete: (id) => api.delete(`/inventory/${id}/`),
  getLowStock: () => api.get('/inventory/low-stock/'),
  getStats: () => api.get('/inventory/stats/'),
};

// SUPPLIER ENDPOINTS
export const supplierAPI = {
  getAll: () => api.get('/suppliers/'),
  getById: (id) => api.get(`/suppliers/${id}/`),
  create: (supplierData) => api.post('/suppliers/', supplierData),
  update: (id, supplierData) => api.put(`/suppliers/${id}/`, supplierData),
  delete: (id) => api.delete(`/suppliers/${id}/`),
  getItems: (id) => api.get(`/suppliers/${id}/items/`),
};


// USER ENDPOINTS (Admin only)
export const userAPI = {
  getAll: () => api.get('/users'),
  getById: (id) => api.get(`/users/${id}`),
  create: (userData) => api.post('/users', userData),
  update: (id, userData) => api.put(`/users/${id}`, userData),
  delete: (id) => api.delete(`/users/${id}`),
  getStats: () => api.get('/users/stats'),
};

// REPORT ENDPOINTS (Admin only)
export const reportAPI = {
  getActivityLogs: (limit = 20) => api.get('/reports/activity-logs', { params: { limit } }),
  downloadInventoryPDF: () => window.open(`${API_BASE_URL}/reports/inventory-pdf`),
  downloadInventoryCSV: () => window.open(`${API_BASE_URL}/reports/inventory-csv`),
  downloadLowStockPDF: () => window.open(`${API_BASE_URL}/reports/low-stock-pdf`),
  downloadSuppliersCSV: () => window.open(`${API_BASE_URL}/reports/suppliers-csv`),
};

export default api;