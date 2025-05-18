import React, { useEffect, useState } from 'react';
// No auth imports needed as redirect is auto-handled
import { useNavigate } from 'react-router-dom';

// Component that handles OAuth callback
const AuthCallback: React.FC = () => {
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    // Parse the URL hash to get access token
    const handleAuth = async () => {
      try {
        // Auto-handle the redirect in Amplify v6
        // The URL parameters will be automatically processed
        
        // Wait a moment to ensure Amplify has time to process the auth state
        setTimeout(() => {
          // Redirect to home page after authentication
          navigate('/');
        }, 1000);
      } catch (err) {
        console.error('Authentication error:', err);
        setError('Failed to authenticate. Please try again.');
      }
    };

    handleAuth();
  }, [navigate]);

  // Show loading or error message
  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
      {error ? (
        <div>
          <h3>Authentication Error</h3>
          <p>{error}</p>
          <button onClick={() => navigate('/')}>Go to Homepage</button>
        </div>
      ) : (
        <div>
          <p>Completing authentication, please wait...</p>
        </div>
      )}
    </div>
  );
};

export default AuthCallback;