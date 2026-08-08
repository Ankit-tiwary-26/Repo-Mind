import React from 'react';
import { FolderGit2, FileCode2, Database, Code2 } from 'lucide-react';
import ProjectCard from '../components/ProjectCard';
import HealthScore from '../components/HealthScore';

export default function Dashboard({ projects, onNewProject }) {
  const totalProjects = projects.length;
  const totalFiles = projects.reduce((acc, p) => acc + (p.files_indexed || 0), 0);
  const totalChunks = projects.reduce((acc, p) => acc + (p.chunk_count || 0), 0);
  const languages = new Set();
  projects.forEach(p => {
    if (p.meta && p.meta.languages) {
      p.meta.languages.forEach(l => languages.add(l));
    }
  });

  return (
    <div style={{ padding: '40px', maxWidth: '1200px', margin: '0 auto' }}>
      <div style={{ marginBottom: '40px', animation: 'fadeIn 0.5s ease-out' }}>
        <h1 style={{ 
          fontSize: '48px', 
          fontWeight: 800, 
          marginBottom: '12px',
          background: 'linear-gradient(to right, var(--primary), var(--secondary))',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent'
        }}>
          RepoMind AI
        </h1>
        <p style={{ fontSize: '20px', color: 'var(--text-secondary)' }}>AI-powered codebase intelligence</p>
      </div>

      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', 
        gap: '24px', 
        marginBottom: '48px' 
      }}>
        {[
          { label: 'Total Projects', value: totalProjects, icon: FolderGit2, color: 'var(--primary)' },
          { label: 'Files Indexed', value: totalFiles, icon: FileCode2, color: 'var(--secondary)' },
          { label: 'Total Chunks', value: totalChunks, icon: Database, color: 'var(--accent)' },
          { label: 'Languages', value: languages.size || 3, icon: Code2, color: '#22c55e' }
        ].map((stat, i) => (
          <div key={i} className="glass-card" style={{ 
            padding: '24px', 
            display: 'flex', 
            alignItems: 'center', 
            gap: '20px',
            animation: `slideUp 0.5s ease-out ${i * 0.1}s both`
          }}>
            <div style={{ 
              background: `${stat.color}15`, 
              padding: '16px', 
              borderRadius: '16px',
              color: stat.color,
              boxShadow: `0 0 20px ${stat.color}20`
            }}>
              <stat.icon size={32} />
            </div>
            <div>
              <div style={{ fontSize: '32px', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '4px' }}>{stat.value}</div>
              <div style={{ color: 'var(--text-muted)', fontSize: '14px', fontWeight: 500 }}>{stat.label}</div>
            </div>
          </div>
        ))}
      </div>

      <div style={{ animation: 'fadeIn 0.5s ease-out 0.4s both' }}>
        <h2 style={{ fontSize: '24px', marginBottom: '24px', color: 'var(--text-primary)' }}>Recent Projects</h2>
        {projects.length === 0 ? (
          <div className="glass-card" style={{ padding: '64px', textAlign: 'center', borderStyle: 'dashed' }}>
            <FolderGit2 size={64} color="var(--text-muted)" style={{ margin: '0 auto 24px', opacity: 0.5 }} />
            <h3 style={{ fontSize: '20px', marginBottom: '12px', color: 'var(--text-secondary)' }}>No projects indexed yet</h3>
            <p style={{ color: 'var(--text-muted)', marginBottom: '32px' }}>Clone a repository or upload a zip file to get started.</p>
            <button className="btn-primary" onClick={onNewProject} style={{ padding: '12px 32px', fontSize: '16px' }}>
              Get Started
            </button>
          </div>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '20px' }}>
            {projects.map(p => (
              <div key={p.project_id} style={{ transform: 'scale(1.02)' }}>
                <ProjectCard project={p} />
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
