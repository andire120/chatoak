import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000'; // 백엔드 FastAPI 서버 주소

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('jwt_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export const authApi = {
  register: (username: string, password_hash: string) =>
    api.post('/register', { username, password_hash }),
  login: (username: string, password_hash: string) =>
    api.post('/login', { username, password_hash }),
};

export const roomsApi = {
  getRooms: () => api.get('/rooms'),
  createRoom: (name: string) => api.post('/rooms', { name }),
  getMessages: (roomId: string) => api.get(`/rooms/${roomId}/messages`),
};

export const createWebSocket = (roomId: string, token: string) => {
  // WebSocket URL은 FastAPI 서버의 WS 엔드포인트와 일치해야 합니다.
  const wsUrl = `ws://localhost:8000/ws/chat/${roomId}?token=${token}`;
  return new WebSocket(wsUrl);
};