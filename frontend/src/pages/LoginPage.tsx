import React from 'react';
import { useAuth } from '../context/AuthContext';
import { Navigate } from 'react-router-dom';

const LoginPage: React.FC = () => {
  const { isAuthenticated, isLoading, signIn } = useAuth();

  // Redirect if already authenticated
  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  return (
    <div style={{ 
      display: 'flex', 
      flexDirection: 'column',
      justifyContent: 'center', 
      alignItems: 'center', 
      height: '100vh',
      padding: '20px'
    }}>
      <h1>Ping-Pong Leaderboard</h1>
      <h2>Sign In</h2>
      
      {isLoading ? (
        <p>Loading...</p>
      ) : (
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: '20px',
          marginTop: '30px'
        }}>
          <p>Sign in with your Google account to access the leaderboard.</p>
          <button 
            onClick={signIn}
            style={{
              padding: '10px 20px',
              fontSize: '16px',
              backgroundColor: '#4285F4',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            Sign In with Google
          </button>
        </div>
      )}
    </div>
  );
};

export default LoginPage;