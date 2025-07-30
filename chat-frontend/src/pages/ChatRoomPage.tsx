import React, { useEffect, useState, useRef, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { createWebSocket, roomsApi } from '../services/api';
import Input from '../components/Input';
import Button from '../components/Button';
import { useAuth } from '../contexts/AuthContext';

interface Message {
  username: string;
  message: string;
  timestamp?: string; // 백엔드에서 내려줄 경우 대비
}

const ChatRoomPage: React.FC = () => {
  const { roomId } = useParams<{ roomId: string }>();
  const navigate = useNavigate();
  const { token, isAuthenticated } = useAuth();
  const [messages, setMessages] = useState<Message[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const ws = useRef<WebSocket | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // 이전 메시지 로드
  const fetchPreviousMessages = useCallback(async () => {
    if (!roomId) return;
    try {
      const response = await roomsApi.getMessages(roomId);
      // 백엔드에서 받은 메시지 형식이 { sender_username, content } 일 수 있으므로 변환
      const formattedMessages = response.data.map((msg: any) => ({
        username: msg.sender_username,
        message: msg.content,
        timestamp: msg.timestamp,
      }));
      setMessages(formattedMessages);
    } catch (err) {
      console.error('이전 메시지 로드 실패:', err);
      setError('이전 메시지를 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  }, [roomId]);

  useEffect(() => {
    if (!isAuthenticated || !token || !roomId) {
      navigate('/login');
      return;
    }

    fetchPreviousMessages();

    // WebSocket 연결
    ws.current = createWebSocket(roomId, token);

    ws.current.onopen = () => {
      console.log('WebSocket 연결됨');
      setError(null);
    };

    ws.current.onmessage = (event) => {
      const receivedMessage: Message = JSON.parse(event.data);
      setMessages((prevMessages) => [...prevMessages, receivedMessage]);
    };

    ws.current.onclose = (event) => {
      console.log('WebSocket 연결 끊김:', event.code, event.reason);
      if (event.code === 1000) { // 정상 종료
        // navigate('/rooms'); // 방 나갈 때
      } else {
        setError('채팅 서버 연결이 끊겼습니다. 다시 시도해주세요.');
      }
    };

    ws.current.onerror = (err) => {
      console.error('WebSocket 오류:', err);
      setError('WebSocket 연결 중 오류 발생.');
      ws.current?.close();
    };

    // 컴포넌트 언마운트 시 WebSocket 연결 해제
    return () => {
      if (ws.current && ws.current.readyState === WebSocket.OPEN) {
        ws.current.close(1000, "User left the chat"); // 정상 종료 코드 1000
      }
    };
  }, [roomId, token, isAuthenticated, navigate, fetchPreviousMessages]);

  // 메시지 업데이트 시 스크롤 하단으로 이동
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    if (ws.current && newMessage.trim()) {
      const messagePayload = { message: newMessage }; // 백엔드에서 username은 JWT로 추출
      ws.current.send(JSON.stringify(messagePayload));
      setNewMessage('');
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <p>메시지를 로드 중입니다...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col items-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-xl w-full bg-white p-8 rounded-lg shadow-md flex flex-col h-[80vh]">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-900">채팅방: {roomId}</h2>
          <Button onClick={() => navigate('/')} className="w-auto px-4 py-2 bg-gray-600 hover:bg-gray-700">
            방 목록으로
          </Button>
        </div>

        {error && <p className="text-red-500 text-center mb-4">{error}</p>}

        <div className="flex-grow overflow-y-auto border border-gray-200 rounded-md p-4 mb-4 bg-gray-50">
          {messages.length === 0 && !loading && !error ? (
            <p className="text-gray-500 text-center">아직 메시지가 없습니다. 첫 메시지를 보내보세요!</p>
          ) : (
            messages.map((msg, index) => (
              <div key={index} className="mb-2">
                <span className="font-semibold text-indigo-700">{msg.username}:</span>{' '}
                <span className="text-gray-800">{msg.message}</span>
                {msg.timestamp && <span className="text-xs text-gray-400 ml-2">{new Date(msg.timestamp).toLocaleTimeString()}</span>}
              </div>
            ))
          )}
          <div ref={messagesEndRef} /> {/* 스크롤을 위한 더미 엘리먼트 */}
        </div>

        <form onSubmit={handleSendMessage} className="flex space-x-2">
          <Input
            type="text"
            placeholder="메시지를 입력하세요..."
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            className="flex-grow"
          />
          <Button type="submit" className="w-auto px-6 py-2">
            전송
          </Button>
        </form>
      </div>
    </div>
  );
};

export default ChatRoomPage;