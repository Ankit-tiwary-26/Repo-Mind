import React from 'react';
import { NavLink } from 'react-router-dom';
import { BrainCircuit, Plus, LayoutDashboard } from 'lucide-react';
import ProjectCard from './ProjectCard';

export default function Sidebar({ projects, onNewProject, refreshProjects }) {
  return (
    <aside style={{
      width: '280px',
      background: 'var(--bg-secondary)',
      borderRight: '1px solid var(--border)',
      display: 'flex',
      flexDirection: 'column',
      height: '100%',
    }}>
      <div style={{ padding: '24px 20px', display: 'flex', alignItems: 'center', gap: '12px' }}>
        <BrainCircuit size={28} color="var(--primary)" style={{ filter: 'drop-shadow(0 0 8px rgba(139,92,246,0.5))' }} />
        <h1 style={{ fontSize: '20px', fontWeight: 700, margin: 0, background: 'linear-gradient(90deg, var(--primary-light), var(--secondary-light))', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
          RepoMind AI
        </h1>
      </div>
      
      <div style={{ padding: '0 20px 20px' }}>
        <button className="btn-primary" onClick={onNewProject} style={{ width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', padding: '10px' }}>
          <Plus size={18} /> New Project
        </button>
      </div>

      <div style={{ flex: 1, overflowY: 'auto', padding: '0 20px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {projects.map(p => (
          <NavLink 
            key={p.project_id} 
            to={`/chat/${p.project_id}`} 
            style={{ textDecoration: 'none', color: 'inherit' }}
          >
            {({ isActive }) => (
              <ProjectCard project={p} isActive={isActive} refreshProjects={refreshProjects} />
            )}
          </NavLink>
        ))}
      </div>

      <div style={{ padding: '20px', borderTop: '1px solid var(--border)' }}>
        <NavLink 
          to="/" 
          className="btn-ghost glass-card"
          style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '12px', textDecoration: 'none' }}
        >
          <LayoutDashboard size={20} />
          <span>Dashboard</span>
        </NavLink>
      </div>
    </aside>
  );
}
