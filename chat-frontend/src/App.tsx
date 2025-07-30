import React, { type JSX } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import ChatRoomsPage from './pages/ChatRoomsPage';
import ChatRoomPage from './pages/ChatRoomPage';
import { AuthProvider, useAuth } from './contexts/AuthContext'; // AuthProvider 추가

const ProtectedRoute: React.FC<{ children: JSX.Element }> = ({ children }) => {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? children : <Navigate to="/login" />;
};

function App() {
  return (
    <Router>
      <AuthProvider> {/* AuthProvider로 감싸서 전역 인증 상태 제공 */}
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/" element={<ProtectedRoute><ChatRoomsPage /></ProtectedRoute>} />
          <Route path="/rooms/:roomId" element={<ProtectedRoute><ChatRoomPage /></ProtectedRoute>} />
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </AuthProvider>
    </Router>
  );
}

export default App;