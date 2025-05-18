import React from 'react';
import { Link } from 'react-router-dom';

const UnauthorizedPage: React.FC = () => {
  return (
    <div style={{ 
      display: 'flex', 
      flexDirection: 'column',
      justifyContent: 'center', 
      alignItems: 'center', 
      height: '100vh',
      padding: '20px'
    }}>
      <h1>Access Denied</h1>
      <p>You don't have permission to access this page.</p>
      <p>Please contact an administrator if you believe this is an error.</p>
      
      <Link to="/" style={{ marginTop: '20px' }}>
        Return to Home
      </Link>
    </div>
  );
};

export default UnauthorizedPage;