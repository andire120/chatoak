import { useNavigate } from 'react-router-dom';
import Button from '../components/Button';
import './MainPage.css';

const MainPage: React.FC = () => {
const navigate = useNavigate();

return (
<div className="container">
    <div className='box'> 
        <div className="w-full h-full text-center mb-[5px]">
            <div>
            <img src="/sol_bird.png" alt="sol_bird" className='w-[80%] mr-[5px]'/>
            <p className='name'>Chatoak</p>
            </div>
                <Button onClick={() => navigate('/login')} className="btn">
                시작하기
            </Button>
        </div>
    </div>
</div>
);
};

export default MainPage;