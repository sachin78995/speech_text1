import React from 'react';
import './Header.css';

const Header = () => {
  return (
    <header className="header">
      <div className="header-content">
        <div className="logo">
          <div className="logo-icon">🎤</div>
          <h1>Speech-to-Text</h1>
        </div>
        <p className="subtitle">Offline Speech Recognition with Grammar Correction</p>
      </div>
    </header>
  );
};

export default Header;

