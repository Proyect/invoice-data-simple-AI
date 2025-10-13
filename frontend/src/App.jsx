import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { Layout } from 'antd';
import AppLayout from './components/Layout';
import Dashboard from './components/Dashboard';
import DocumentUpload from './components/DocumentUpload';
import DocumentList from './components/DocumentList';
import './index.css';

function App() {
  return (
    <AppLayout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/upload" element={<DocumentUpload />} />
        <Route path="/documents" element={<DocumentList />} />
      </Routes>
    </AppLayout>
  );
}

export default App;
