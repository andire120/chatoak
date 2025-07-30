import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { roomsApi } from '../services/api';
import Button from '../components/Button';
import Input from '../components/Input';
import { useAuth } from '../contexts/AuthContext';

interface ChatRoom {
  id: string;
  name: string;
  created_by: string; // created_by 필드가 필요할 경우
}

const ChatRoomsPage: React.FC = () => {
  const [rooms, setRooms] = useState<ChatRoom[]>([]);
  const [newRoomName, setNewRoomName] = useState('');
  const navigate = useNavigate();
  const { logout } = useAuth();

  useEffect(() => {
    fetchRooms();
  }, []);

  const fetchRooms = async () => {
    try {
      const response = await roomsApi.getRooms();
      setRooms(response.data);
    } catch (error) {
      console.error('채팅방 목록을 불러오는데 실패했습니다:', error);
      alert('채팅방 목록 로드 실패.');
    }
  };

  const handleCreateRoom = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newRoomName.trim()) return;
    try {
      await roomsApi.createRoom(newRoomName);
      setNewRoomName('');
      fetchRooms(); // 방 생성 후 목록 새로고침
    } catch (error) {
      console.error('채팅방 생성에 실패했습니다:', error);
      alert('채팅방 생성 실패.');
    }
  };

  const handleRoomClick = (roomId: string) => {
    navigate(`/rooms/${roomId}`);
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col items-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-xl w-full bg-white p-8 rounded-lg shadow-md">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-3xl font-extrabold text-gray-900">채팅방 목록</h2>
          <Button onClick={handleLogout} className="w-auto px-4 py-2 bg-red-600 hover:bg-red-700">
            로그아웃
          </Button>
        </div>

        <form onSubmit={handleCreateRoom} className="flex mb-6 space-x-2">
          <Input
            type="text"
            placeholder="새 채팅방 이름"
            value={newRoomName}
            onChange={(e) => setNewRoomName(e.target.value)}
            className="flex-grow"
          />
          <Button type="submit" className="w-auto px-6 py-2">
            방 만들기
          </Button>
        </form>

        <ul className="space-y-4">
          {rooms.length === 0 ? (
            <p className="text-gray-600 text-center">생성된 채팅방이 없습니다. 새로운 방을 만들어 보세요!</p>
          ) : (
            rooms.map((room) => (
              <li
                key={room.id}
                className="bg-gray-50 p-4 rounded-md shadow-sm hover:bg-gray-100 cursor-pointer transition duration-150 ease-in-out"
                onClick={() => handleRoomClick(room.id)}
              >
                <h3 className="text-lg font-semibold text-gray-800">{room.name}</h3>
                {/* <p className="text-sm text-gray-500">생성자: {room.created_by}</p> */}
              </li>
            ))
          )}
        </ul>
      </div>
    </div>
  );
};

export default ChatRoomsPage;