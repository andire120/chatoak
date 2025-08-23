import React, { type JSX } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import MainPage from './pages/mainPage'; // MainPage로 수정
import LoginPage from './pages/LoginPage';
import ChatRoomsPage from './pages/ChatRoomsPage';
import ChatRoomPage from './pages/ChatRoomPage';
import { AuthProvider, useAuth } from './contexts/AuthContext'; // AuthProvider 추가

const ProtectedRoute: React.FC<{ children: JSX.Element }> = ({ children }) => {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? children : <Navigate to="/main" />;
};

function App() {
  return (
    <Router>
      <AuthProvider> 
        <Routes>
          <Route path="/main" element={<MainPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/" element={<ProtectedRoute><Navigate to="/rooms" /></ProtectedRoute>} />
          <Route path="/rooms" element={<ProtectedRoute><ChatRoomsPage /></ProtectedRoute> } />
          <Route path="/rooms/:roomId" element={<ProtectedRoute><ChatRoomPage /></ProtectedRoute>} />
          <Route path="*" element={<Navigate to="/main" />} />
        </Routes>
      </AuthProvider>
    </Router>
  );
}

export default App;
