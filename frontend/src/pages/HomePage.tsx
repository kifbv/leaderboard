import React from 'react';
import { useAuth } from '../context/AuthContext';

const HomePage: React.FC = () => {
  const { user, isAuthenticated, signIn, signOut } = useAuth();

  return (
    <div>
      <h1>Ping-Pong Leaderboard</h1>
      
      {isAuthenticated ? (
        <div>
          <p>Welcome, {user?.username}!</p>
          <button onClick={signOut}>Sign Out</button>
        </div>
      ) : (
        <div>
          <p>Sign in to view and manage leaderboards</p>
          <button onClick={signIn}>Sign In with Google</button>
        </div>
      )}
      
      <div style={{ marginTop: '2rem' }}>
        <h2>Leaderboard Features</h2>
        <ul>
          <li>View player rankings</li>
          <li>Track game results</li>
          <li>Manage tournaments</li>
          <li>Analyze performance statistics</li>
        </ul>
      </div>
    </div>
  );
};

export default HomePage;