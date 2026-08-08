import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { getProjectSummary } from '../api';
import ChatPanel from '../components/ChatPanel';
import HealthScore from '../components/HealthScore';
import { FolderGit2, FileCode2, Database } from 'lucide-react';

export default function Chat() {
  const { projectId } = useParams();
  const [project, setProject] = useState(null);

  useEffect(() => {
    const fetchSummary = async () => {
      try {
        const data = await getProjectSummary(projectId);
        setProject(data);
      } catch (err) {
        console.error('Error fetching project summary:', err);
      }
    };
    if (projectId) fetchSummary();
  }, [projectId]);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      {/* Header */}
      <header className="glass-card" style={{ 
        padding: '20px 32px', 
        borderRadius: 0, 
        borderLeft: 'none', 
        borderRight: 'none', 
        borderTop: 'none',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        zIndex: 10
      }}>
        <div>
          <h2 style={{ margin: '0 0 8px 0', fontSize: '20px', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <FolderGit2 color="var(--primary)" />
            {project?.repo_url ? project.repo_url.split('/').pop().replace('.git', '') : projectId}
          </h2>
          <div style={{ display: 'flex', gap: '20px', color: 'var(--text-muted)', fontSize: '14px' }}>
            <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <FileCode2 size={16} /> {project?.files_indexed || 0} files
            </span>
            <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Database size={16} /> {project?.chunk_count || 0} chunks
            </span>
          </div>
        </div>
        
        <div style={{ transform: 'scale(0.8)', transformOrigin: 'right center' }}>
          <HealthScore score={85} label="Codebase Health" />
        </div>
      </header>

      {/* Chat Area */}
      <div style={{ flex: 1, overflow: 'hidden' }}>
        <ChatPanel projectId={projectId} />
      </div>
    </div>
  );
}
