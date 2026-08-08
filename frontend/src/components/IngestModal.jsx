import React, { useState } from 'react';
import { X, UploadCloud, Loader2 } from "lucide-react";
import { cloneRepo, uploadZip } from '../api';

export default function IngestModal({ onClose, onSuccess }) {
  const [tab, setTab] = useState('clone');
  const [gitUrl, setGitUrl] = useState('');
  const [githubToken, setGithubToken] = useState('');
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [successData, setSuccessData] = useState(null);

  const handleClone = async (e) => {
    e.preventDefault();
    if (!gitUrl) return;
    try {
      setLoading(true);
      setError('');
      const data = await cloneRepo(gitUrl, githubToken);
      setSuccessData(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) return;
    try {
      setLoading(true);
      setError('');
      const data = await uploadZip(file);
      setSuccessData(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
      background: 'rgba(6, 6, 15, 0.8)', backdropFilter: 'blur(4px)',
      display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000,
      animation: 'fadeIn 0.2s ease-out'
    }}>
      <div className="glass-card" style={{
        width: '500px', maxWidth: '90%', padding: '24px', position: 'relative',
        animation: 'slideUp 0.3s ease-out'
      }}>
        <button className="btn-ghost" onClick={onClose} style={{ position: 'absolute', top: '16px', right: '16px', padding: '4px' }}>
          <X size={20} />
        </button>

        <h2 style={{ marginBottom: '20px', fontSize: '24px' }}>Add Project</h2>

        {successData ? (
          <div style={{ textAlign: 'center', padding: '20px' }}>
            <h3 style={{ color: 'var(--secondary-light)', marginBottom: '10px' }}>Success!</h3>
            <p style={{ color: 'var(--text-secondary)' }}>Files Indexed: {successData.files_indexed}</p>
            <p style={{ color: 'var(--text-secondary)', marginBottom: '20px' }}>Chunks Indexed: {successData.chunks_indexed}</p>
            <button className="btn-primary" onClick={onSuccess}>Continue</button>
          </div>
        ) : (
          <>
            <div style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
              <button 
                className={tab === 'clone' ? 'btn-primary' : 'btn-ghost'} 
                onClick={() => setTab('clone')}
                style={{ flex: 1 }}
              >
                <UploadCloud size={16} style={{ display: 'inline', marginRight: '8px' }}/> Clone from GitHub
              </button>
              <button 
                className={tab === 'upload' ? 'btn-primary' : 'btn-ghost'} 
                onClick={() => setTab('upload')}
                style={{ flex: 1 }}
              >
                <UploadCloud size={16} style={{ display: 'inline', marginRight: '8px' }}/> Upload ZIP
              </button>
            </div>

            {error && <div style={{ color: 'var(--accent)', padding: '10px', background: 'rgba(244,114,182,0.1)', borderRadius: '8px', marginBottom: '16px' }}>{error}</div>}

            {tab === 'clone' && (
              <form onSubmit={handleClone}>
                <div style={{ marginBottom: '16px' }}>
                  <label style={{ display: 'block', marginBottom: '8px', color: 'var(--text-secondary)', fontSize: '14px' }}>Git Repository URL</label>
                  <input 
                    type="text" 
                    placeholder="https://github.com/user/repo"
                    value={gitUrl} 
                    onChange={e => setGitUrl(e.target.value)}
                    style={{ width: '100%', padding: '12px', borderRadius: '8px', border: '1px solid var(--border)', background: 'var(--bg-input)', color: '#fff', outline: 'none' }}
                  />
                </div>
                <div style={{ marginBottom: '20px' }}>
                  <label style={{ display: 'block', marginBottom: '8px', color: 'var(--text-secondary)', fontSize: '14px' }}>GitHub Token (Optional)</label>
                  <input 
                    type="password" 
                    placeholder="ghp_..."
                    value={githubToken} 
                    onChange={e => setGithubToken(e.target.value)}
                    style={{ width: '100%', padding: '12px', borderRadius: '8px', border: '1px solid var(--border)', background: 'var(--bg-input)', color: '#fff', outline: 'none' }}
                  />
                </div>
                <button type="submit" className="btn-primary" style={{ width: '100%', padding: '12px' }} disabled={loading}>
                  {loading ? <Loader2 className="spin" size={20} style={{ animation: 'spin 1s linear infinite', margin: '0 auto' }} /> : 'Clone Repository'}
                </button>
              </form>
            )}

            {tab === 'upload' && (
              <form onSubmit={handleUpload}>
                <div style={{ marginBottom: '20px', border: '2px dashed var(--border)', borderRadius: '12px', padding: '40px', textAlign: 'center', cursor: 'pointer', background: 'var(--bg-input)' }}>
                  <input 
                    type="file" 
                    accept=".zip"
                    onChange={e => setFile(e.target.files[0])}
                    style={{ display: 'none' }}
                    id="file-upload"
                  />
                  <label htmlFor="file-upload" style={{ cursor: 'pointer' }}>
                    <UploadCloud size={40} color="var(--primary)" style={{ marginBottom: '10px' }} />
                    <p>{file ? file.name : 'Click or drag a .zip file here'}</p>
                  </label>
                </div>
                <button type="submit" className="btn-primary" style={{ width: '100%', padding: '12px' }} disabled={!file || loading}>
                  {loading ? <Loader2 size={20} style={{ animation: 'spin 1s linear infinite', margin: '0 auto' }} /> : 'Upload and Index'}
                </button>
              </form>
            )}
          </>
        )}
      </div>
    </div>
  );
}
