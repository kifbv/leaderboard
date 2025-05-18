import React, { createContext, useState, useEffect, useContext } from 'react';
import { 
  getCurrentUser, 
  signOut as amplifySignOut,
  fetchUserAttributes,
  signInWithRedirect
} from 'aws-amplify/auth';
import { AuthUser } from '../types/models';

// Define context type
interface AuthContextType {
  user: AuthUser | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  signIn: () => void;
  signOut: () => Promise<void>;
  checkIsAdmin: (user: AuthUser) => boolean;
}

// Create context with default values
const AuthContext = createContext<AuthContextType>({
  user: null,
  isAuthenticated: false,
  isLoading: true,
  signIn: () => {},
  signOut: async () => {},
  checkIsAdmin: () => false,
});

// Admin emails from environment
const ADMIN_EMAILS = process.env.REACT_APP_ADMIN_EMAILS?.split(',') || [];

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Check if user is admin
  const checkIsAdmin = React.useCallback((user: AuthUser): boolean => {
    return ADMIN_EMAILS.includes(user.email);
  }, []);

  // Fetch current authenticated user
  // Using useCallback to prevent recreation of the function on each render
  const fetchUser = React.useCallback(async () => {
    try {
      setIsLoading(true);
      
      const amplifyUser = await getCurrentUser();
      const userAttributes = await fetchUserAttributes();
      
      const authUser: AuthUser = {
        username: amplifyUser.username,
        email: userAttributes.email || '',
        isAdmin: checkIsAdmin({ 
          username: amplifyUser.username, 
          email: userAttributes.email || '',
          isAdmin: false,
          attributes: userAttributes 
        }),
        attributes: userAttributes,
      };
      
      setUser(authUser);
    } catch (error) {
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  }, [checkIsAdmin]);

  // Initialize auth state
  useEffect(() => {
    fetchUser();
    
    // Check for auth changes every minute
    const interval = setInterval(() => {
      fetchUser();
    }, 60000);
    
    return () => clearInterval(interval);
  }, [fetchUser]);

  // Sign in with Google
  const signIn = () => {
    signInWithRedirect({ provider: 'Google' });
  };

  // Sign out
  const signOut = async () => {
    try {
      await amplifySignOut();
      setUser(null);
    } catch (error) {
      console.error('Error signing out:', error);
    }
  };

  return (
    <AuthContext.Provider 
      value={{ 
        user, 
        isAuthenticated: !!user, 
        isLoading, 
        signIn, 
        signOut,
        checkIsAdmin
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

// Custom hook to use auth context
export const useAuth = () => useContext(AuthContext);