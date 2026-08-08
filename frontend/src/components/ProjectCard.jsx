import React from 'react';
import { Trash2 } from 'lucide-react';
import { deleteProject } from '../api';

export default function ProjectCard({ project, isActive, refreshProjects }) {
  const name = project.repo_url ? project.repo_url.split('/').pop().replace('.git', '') : project.project_id;
  const date = new Date(project.created_at).toLocaleDateString();

  const handleDelete = async (e) => {
    e.preventDefault();
    if (window.confirm('Delete this project?')) {
      await deleteProject(project.project_id);
      if (refreshProjects) refreshProjects();
    }
  };

  return (
    <div className="glass-card" style={{
      padding: '16px',
      position: 'relative',
      borderLeft: isActive ? '4px solid var(--primary)' : '1px solid var(--glass-border)',
      boxShadow: isActive ? 'var(--glow-purple)' : 'none',
      background: isActive ? 'var(--bg-card-hover)' : 'var(--glass-bg)'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
        <h3 style={{ margin: 0, fontSize: '16px', fontWeight: 600, color: 'var(--text-primary)', wordBreak: 'break-all' }}>{name}</h3>
        <button className="btn-ghost" onClick={handleDelete} style={{ padding: '4px', color: 'var(--text-muted)' }}>
          <Trash2 size={16} />
        </button>
      </div>
      
      <div style={{ display: 'flex', gap: '8px', marginBottom: '12px', flexWrap: 'wrap' }}>
        <span style={{ fontSize: '12px', padding: '2px 8px', background: 'rgba(139, 92, 246, 0.1)', color: 'var(--primary-light)', borderRadius: '12px', border: '1px solid var(--border)' }}>
          {project.files_indexed} files
        </span>
        <span style={{ fontSize: '12px', padding: '2px 8px', background: 'rgba(6, 182, 212, 0.1)', color: 'var(--secondary-light)', borderRadius: '12px', border: '1px solid rgba(6, 182, 212, 0.2)' }}>
          {project.chunk_count || 0} chunks
        </span>
      </div>

      <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
        Created {date}
      </div>
    </div>
  );
}
