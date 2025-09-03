import React, { useEffect, useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { roomsApi } from '../services/api';
import Button from '../components/Button';
import Input from '../components/Input';
import { useAuth } from '../contexts/AuthContext';
import './ChatRoomsPage.css';
import { AlignJustify } from 'lucide-react';

interface ChatRoom {
  id: string;
  name: string;
  created_by: string;
}

const ChatRoomsPage: React.FC = () => {
  const [rooms, setRooms] = useState<ChatRoom[]>([]);
  const [newRoomName, setNewRoomName] = useState('');
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isCreateFormVisible, setIsCreateFormVisible] = useState(false);
  const navigate = useNavigate();
  const { logout } = useAuth();
  
  // 메뉴 컨테이너의 DOM 요소를 참조하기 위한 ref
  const menuRef = useRef<HTMLDivElement>(null); 

  useEffect(() => {
    fetchRooms();
  }, []);

  useEffect(() => {
    // 메뉴가 열려 있을 때만 이벤트 리스너를 추가
    if (isMenuOpen) {
      document.addEventListener('mousedown', handleOutsideClick);
    }
    
    // 컴포넌트가 언마운트되거나 isMenuOpen 상태가 변경될 때 이벤트 리스너를 정리
    return () => {
      document.removeEventListener('mousedown', handleOutsideClick);
    };
  }, [isMenuOpen]);

  // 바깥 클릭을 감지하는 함수
  const handleOutsideClick = (event: MouseEvent) => {
    // ref에 현재 참조된 요소가 있고, 클릭된 요소가 메뉴 컨테이너 안에 포함되지 않는지 확인
    if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
      setIsMenuOpen(false);
    }
  };

  const fetchRooms = async () => {
    try {
      const response = await roomsApi.getRooms();
      setRooms(response.data);
    } catch (error) {
      // console.error('채팅방 목록을 불러오는데 실패했습니다:', error);
      // alert('채팅방 목록 로드 실패.');
    }
  };

  const handleCreateRoom = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newRoomName.trim()) return;
    try {
      await roomsApi.createRoom(newRoomName);
      setNewRoomName('');
      setIsCreateFormVisible(false);
      fetchRooms();
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
      <header>
        <h2 className="text-3xl font-extrabold text-gray-900 w-[auto]">채팅방 목록</h2>
        <div className="menu-bt" ref={menuRef}> 
          <div 
            onClick={() => setIsMenuOpen(!isMenuOpen)} 
            className='h-[28px]'
            aria-label="메뉴 열기"
          >
            <AlignJustify />
          </div>
          {isMenuOpen && (
            <div className="dropdown">
              <div
                onClick={() => {
                  setIsCreateFormVisible(true);
                  setIsMenuOpen(false);
                }}
                className="menu-dropdown-item"
              >
                새 채팅 만들기
              </div>
              <div
                onClick={handleLogout}
                className="menu-dropdown-item"
              >
                로그아웃
              </div>
            </div>
          )}
        </div>
      </header>
       

        {isCreateFormVisible && (
          <form onSubmit={handleCreateRoom} className="chat-form">
            <Input
              type="text"
              placeholder="새 채팅방 이름"
              value={newRoomName}
              onChange={(e) => setNewRoomName(e.target.value)}
              className="ch-name"
            />
            <div className="bt-con">
              <Button type="submit">
                방 만들기
              </Button>
              <Button type="submit"onClick={() => {setIsCreateFormVisible(false);}}>
                취소
              </Button>
            </div>
            
          </form>
        )}

        <ul className="w-[100vw] flex justify-center">
          {rooms.length === 0 ? (
            <p className="text-gray-600 text-center ">생성된 채팅방이 없습니다.<br />새로운 방을 만들어 보세요!</p>
          ) : (
            rooms.map((room) => (
              <li
                key={room.id}
                className="bg-gray-50 p-4 rounded-md shadow-sm hover:bg-gray-100 cursor-pointer transition duration-150 ease-in-out"
                onClick={() => handleRoomClick(room.id)}
              >
                <h3 className="text-lg font-semibold text-gray-800">{room.name}</h3>
              </li>
            ))
          )}
        </ul>
      </div>
  );
};

export default ChatRoomsPage;