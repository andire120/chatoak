import React, { useEffect, useState, useRef, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { createWebSocket, roomsApi } from '../services/api';
import Input from '../components/Input';
import Button from '../components/Button';
import { useAuth } from '../contexts/AuthContext';

interface Message {
  username: string;
  message: string;
  timestamp?: string;
}

const ChatRoomPage: React.FC = () => {
  const { roomId } = useParams<{ roomId: string }>();
  const navigate = useNavigate();
  const { token, isAuthenticated } = useAuth();
  const [messages, setMessages] = useState<Message[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const ws = useRef<WebSocket | null>(null); // WebSocket 인스턴스
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  // 이전 메시지 로드 (변경 없음, useCallback은 이미 적용됨)
  const fetchPreviousMessages = useCallback(async () => {
    if (!roomId) return;
    try {
      const response = await roomsApi.getMessages(roomId);
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

    // 1. 이전 메시지 로드 (한 번만 호출)
    fetchPreviousMessages();

    // 2. WebSocket 연결 로직 (roomId, token이 변경될 때만 재연결)
    // ws.current가 없거나, 이전 연결이 닫혔을 때만 새 연결 시도
    if (!ws.current || ws.current.readyState === WebSocket.CLOSED) {
      ws.current = createWebSocket(roomId, token);

      // WebSocket 이벤트 리스너 등록
      ws.current.onopen = () => {
        console.log('WebSocket 연결됨');
        setError(null);
      };

      // **메시지 수신 핸들러: 중요한 부분**
      // `setMessages`에 함수형 업데이트를 사용하여 `messages` 상태의 최신 값을 보장
      ws.current.onmessage = (event) => {
        const receivedMessage: Message = JSON.parse(event.data);
        setMessages((prevMessages) => {
          // 중복 메시지 방지 로직 추가 (예: 마지막 메시지와 동일한 경우 무시)
          // 이 부분은 백엔드에서 timestamp를 정확히 내려주거나,
          // 메시지에 고유 ID를 부여하는 것이 더 확실합니다.
          // 현재는 간단히 내용과 유저네임이 같으면 무시
          if (prevMessages.length > 0 && 
              prevMessages[prevMessages.length - 1].message === receivedMessage.message &&
              prevMessages[prevMessages.length - 1].username === receivedMessage.username) {
            return prevMessages; // 중복 메시지로 판단하여 업데이트하지 않음
          }
          return [...prevMessages, receivedMessage];
        });
      };

      ws.current.onclose = (event) => {
        console.log('WebSocket 연결 끊김:', event.code, event.reason);
        if (event.code !== 1000) { // 정상 종료(1000)가 아닐 경우에만 에러 표시
          setError('채팅 서버 연결이 끊겼습니다. 다시 시도해주세요.');
        }
      };

      ws.current.onerror = (err) => {
        console.error('WebSocket 오류:', err);
        setError('WebSocket 연결 중 오류 발생.');
        ws.current?.close(); // 오류 발생 시 연결 강제 종료
      };
    }


    // 3. 컴포넌트 언마운트 시 WebSocket 연결 해제 및 정리
    return () => {
      // 컴포넌트 언마운트 시에만 WebSocket을 닫고, useRef 값을 초기화
      // StrictMode의 이중 렌더링 시에는 cleanup이 호출되지만, 바로 effect가 다시 실행되므로
      // 이때는 close하지 않고 ws.current가 유효한지 확인하는 것이 중요합니다.
      // (이 로직은 RoomId나 token이 변경되어 재연결되는 경우에만 필요)
      if (ws.current && ws.current.readyState === WebSocket.OPEN) {
        ws.current.close(1000, "User left the chat");
        console.log('WebSocket 정리: 연결 닫힘');
      }
      ws.current = null; // useRef 초기화 (다음 마운트 시 새 연결 생성 보장)
      setError(null); // 에러 상태 초기화
    };
  }, [roomId, token, isAuthenticated, navigate, fetchPreviousMessages]); // 의존성 배열에 fetchPreviousMessages 포함

  // 메시지 업데이트 시 스크롤 하단으로 이동 (변경 없음)
  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]); // scrollToBottom을 의존성에 추가 (useCallback으로 감쌌으므로 안전)

  // 메시지 전송 핸들러 (변경 없음)
  const handleSendMessage = useCallback((e: React.FormEvent) => {
    e.preventDefault();
    if (ws.current && ws.current.readyState === WebSocket.OPEN && newMessage.trim()) {
      const messagePayload = { message: newMessage };
      ws.current.send(JSON.stringify(messagePayload));
      setNewMessage('');
    } else {
      console.warn("WebSocket is not open or message is empty. Cannot send.");
      if (ws.current && ws.current.readyState === WebSocket.CLOSED) {
          setError('채팅 서버와 연결이 끊어졌습니다. 페이지를 새로고침 해주세요.');
      }
    }
  }, [newMessage]); // newMessage가 변경될 때마다 함수 재생성

  // ... (JSX 렌더링 부분은 동일) ...
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
          <Button onClick={() => navigate('/rooms')} className="w-auto px-4 py-2 bg-gray-600 hover:bg-gray-700">
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
                {/* 사용자 이름과 메시지 사이에 공백 추가 */}
                <span className="font-semibold text-indigo-700">{msg.username} : </span>
                <span className="text-gray-800">{msg.message}</span>
                {/* 타임스탬프 포맷 변경: 'ㅇ (오전 11:50:12)' */}
                {msg.timestamp && (
                  <span className="text-xs text-gray-400 ml-2">
                    &nbsp;&nbsp;( {new Date(msg.timestamp).toLocaleTimeString()} )
                  </span>
                )}
              </div>
            ))
          )}
          <div ref={messagesEndRef} />
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