import React from 'react';
import type { ButtonHTMLAttributes } from 'react';
import './Button.css'; // Assuming you have a CSS file for button styles

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: React.ReactNode;
}

const Button: React.FC<ButtonProps> = ({ children, className, ...rest }) => {
  return (
    <button
      className={`button ${className}`}
      {...rest}
    >
      {children}
    </button>
  );
};

export default Button;