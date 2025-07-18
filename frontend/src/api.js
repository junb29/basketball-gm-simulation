import axios from 'axios';

const api = axios.create({
  baseURL: '',  // Match running FastAPI backend
});

export default api;
