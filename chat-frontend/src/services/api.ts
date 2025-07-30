// src/services/api.ts
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
  // 여기서 password_hash를 password로 변경합니다.
  register: (username: string, password: string) => // <-- 여기 변경
    api.post('/register', { username, password }),   // <-- 그리고 여기 변경 (객체 리터럴 내부도)
  // 여기서 password_hash를 password로 변경합니다.
  login: (username: string, password: string) =>     // <-- 여기 변경
    api.post('/login', { username, password }),      // <-- 그리고 여기 변경 (객체 리터럴 내부도)
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