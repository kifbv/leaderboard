import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { configureAmplify } from './utils/amplify-config';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import HomePage from './pages/HomePage';
import LoginPage from './pages/LoginPage';
import UnauthorizedPage from './pages/UnauthorizedPage';
import AuthCallback from './components/AuthCallback';
import './App.css';

// Initialize Amplify configuration
configureAmplify();

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <Routes>
            {/* Public routes */}
            <Route path="/" element={<HomePage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/callback" element={<AuthCallback />} />
            <Route path="/unauthorized" element={<UnauthorizedPage />} />
            
            {/* Protected routes for regular users */}
            <Route element={<ProtectedRoute />}>
              <Route path="/profile" element={<div>Profile Page (Protected)</div>} />
              <Route path="/games" element={<div>Games Page (Protected)</div>} />
            </Route>
            
            {/* Protected routes for admins */}
            <Route element={<ProtectedRoute requireAdmin={true} />}>
              <Route path="/admin" element={<div>Admin Page (Admin Only)</div>} />
            </Route>
            
            {/* Catch-all route */}
            <Route path="*" element={<div>Page Not Found</div>} />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;