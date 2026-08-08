import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import Chat from './pages/Chat';
import IngestModal from './components/IngestModal';
import { listProjects } from './api';

export default function App() {
  const [projects, setProjects] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [loading, setLoading] = useState(true);

  const fetchProjects = async () => {
    try {
      setLoading(true);
      const data = await listProjects();
      setProjects(data || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProjects();
  }, []);

  return (
    <BrowserRouter>
      <div style={{ display: 'flex', height: '100vh', width: '100vw', overflow: 'hidden' }}>
        <Sidebar 
          projects={projects} 
          onNewProject={() => setIsModalOpen(true)} 
          refreshProjects={fetchProjects}
        />
        <main style={{ flex: 1, overflowY: 'auto', position: 'relative' }}>
          <Routes>
            <Route path="/" element={<Dashboard projects={projects} onNewProject={() => setIsModalOpen(true)} />} />
            <Route path="/chat/:projectId" element={<Chat />} />
          </Routes>
        </main>
        {isModalOpen && (
          <IngestModal 
            onClose={() => setIsModalOpen(false)} 
            onSuccess={() => {
              setIsModalOpen(false);
              fetchProjects();
            }} 
          />
        )}
      </div>
    </BrowserRouter>
  );
}
