import React from 'react';
import './App.css';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import SignUp from './pages/signUp';  
import SignIn from './pages/signIn';
import Dashboard from './pages/Dashboard';
import SubmitOrder from './pages/SubmitOrder';
import OrderTracking from './pages/OrderTracking';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Navigate to="/signin" replace />} />
        <Route path="/signin" element={<SignIn />} />
        <Route path="/signup" element={<SignUp />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/submit-order" element={<SubmitOrder />} />
        <Route path="/orders/:orderId" element={<OrderTracking />} />
      </Routes>
    </Router>
  );
}



export default App;
