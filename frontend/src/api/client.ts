import axios from 'axios';

export const api = axios.create({
  baseURL: '/api',
  timeout: 30_000,
});

api.interceptors.response.use(
  (r) => r,
  (err) => {
    const message =
      err.response?.data?.detail ?? err.message ?? 'Unknown error';
    return Promise.reject(new Error(message));
  },
);
