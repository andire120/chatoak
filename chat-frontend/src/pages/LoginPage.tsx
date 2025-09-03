import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authApi } from '../services/api';
import Input from '../components/Input';
import Button from '../components/Button';
import { useAuth } from '../contexts/AuthContext';
import './LoginPage.css'

const LoginPage: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isRegister, setIsRegister] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();
  const { login } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    try {
      if (isRegister) {
        await authApi.register(username, password);
        alert('회원가입 성공! 로그인해주세요.');
        setIsRegister(false); // 회원가입 성공 후 로그인 폼으로 전환
      } else {
        const response = await authApi.login(username, password);
        login(response.data.access_token);
        navigate('/');
      }
    } catch (err: any) {
      console.error(err);
      setError(err.response?.data?.detail || '오류가 발생했습니다.');
    }
  };

  return (
    <div className="container">
      <div className='box'> 
        <div className="w-full h-full text-center">
          <div>
            <img src="/sol_bird.png" alt="sol_bird" className='w-[50%]'/>
            <h2 className="text">
              {isRegister ? 'SignUp' : 'Login'}
            </h2>
          </div>
          <form className="mt-[20px]" onSubmit={handleSubmit}>
            <Input
              id="username"
              name="username"
              type="text"
              autoComplete="username"
              required
              placeholder="아이디를 입력하세요"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="mb-[8px]"
            />
            <Input
              id="password"
              name="password"
              type="password"
              autoComplete="current-password"
              required
              placeholder="비밀번호를 입력하세요"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="mb-[8px]"
            />
            {error && <p className="text-red-500 text-sm text-center">{error}</p>}
            <div className='mt-[10%]'>
              <Button type="submit">
                {isRegister ? '회원가입' : '로그인'}
              </Button>
            </div>
          </form>
          <div className="text-sm text-center">
            <a
              onClick={() => setIsRegister(!isRegister)}
              className="link"
            >
              {isRegister ? '이미 계정이 있으신가요? 로그인' : '계정이 없으신가요? 회원가입'}
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;