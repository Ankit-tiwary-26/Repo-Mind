import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Send, Loader2, MessageSquare } from 'lucide-react';
import AgentBadge from './AgentBadge';
import { askQuestionStream, getChatHistory } from '../api';

export default function ChatPanel({ projectId }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const history = await getChatHistory(projectId);
        const formatted = history.map(h => [
          { role: 'user', content: h.question },
          { role: 'ai', content: h.answer, agent: h.agent }
        ]).flat();
        setMessages(formatted);
      } catch (err) {
        console.error('Error fetching history:', err);
      }
    };
    if (projectId) fetchHistory();
  }, [projectId]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;
    
    const userMsg = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setIsLoading(true);

    let currentAiMsg = { role: 'ai', content: '', agent: 'qa' };
    setMessages(prev => [...prev, currentAiMsg]);

    try {
      await askQuestionStream(
        projectId, 
        userMsg,
        (chunk) => {
          setIsLoading(false);
          currentAiMsg = { ...currentAiMsg, content: currentAiMsg.content + chunk.chunk, agent: chunk.agent || currentAiMsg.agent };
          setMessages(prev => [...prev.slice(0, -1), currentAiMsg]);
        },
        (done) => {
          setIsLoading(false);
          currentAiMsg = { ...currentAiMsg, content: done.answer, agent: done.agent || currentAiMsg.agent };
          setMessages(prev => [...prev.slice(0, -1), currentAiMsg]);
        },
        (error) => {
          setIsLoading(false);
          currentAiMsg = { ...currentAiMsg, content: currentAiMsg.content + `\n\n**Error:** ${error}` };
          setMessages(prev => [...prev.slice(0, -1), currentAiMsg]);
        }
      );
    } catch (err) {
      setIsLoading(false);
      currentAiMsg = { ...currentAiMsg, content: currentAiMsg.content + `\n\n**Error:** ${err.message}` };
      setMessages(prev => [...prev.slice(0, -1), currentAiMsg]);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', background: 'var(--bg-primary)' }}>
      <div style={{ flex: 1, overflowY: 'auto', padding: '24px', display: 'flex', flexDirection: 'column', gap: '24px' }}>
        {messages.length === 0 ? (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-muted)' }}>
            <MessageSquare size={48} style={{ marginBottom: '16px', opacity: 0.5 }} />
            <h3 style={{ marginBottom: '24px', color: 'var(--text-secondary)' }}>No messages yet</h3>
            <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap', justifyContent: 'center', maxWidth: '600px' }}>
              {["Explain the architecture", "Find security issues", "Suggest tests"].map(suggestion => (
                <button 
                  key={suggestion}
                  className="glass-card" 
                  onClick={() => setInput(suggestion)}
                  style={{ padding: '12px 20px', color: 'var(--primary-light)', border: '1px solid var(--border)' }}
                >
                  "{suggestion}"
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((msg, idx) => (
            <div key={idx} style={{
              alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
              maxWidth: '80%',
              animation: 'slideUp 0.3s ease-out'
            }}>
              {msg.role === 'user' ? (
                <div style={{
                  background: 'var(--primary)',
                  color: '#fff',
                  padding: '12px 20px',
                  borderRadius: '16px',
                  borderBottomRightRadius: '4px',
                  boxShadow: 'var(--glow-purple)',
                  lineHeight: '1.5'
                }}>
                  {msg.content}
                </div>
              ) : (
                <div className="glass-card" style={{
                  padding: '16px 24px',
                  borderRadius: '16px',
                  borderBottomLeftRadius: '4px',
                  lineHeight: '1.6',
                  color: 'var(--text-primary)'
                }}>
                  {msg.agent && <AgentBadge agent={msg.agent} />}
                  <div style={{ marginTop: '8px' }}>
                    <ReactMarkdown
                      components={{
                        code({node, inline, className, children, ...props}) {
                          const match = /language-(\w+)/.exec(className || '')
                          return !inline && match ? (
                            <SyntaxHighlighter
                              style={vscDarkPlus}
                              language={match[1]}
                              PreTag="div"
                              customStyle={{ borderRadius: '8px', margin: '16px 0' }}
                              {...props}
                            >
                              {String(children).replace(/\n$/, '')}
                            </SyntaxHighlighter>
                          ) : (
                            <code style={{ background: 'rgba(0,0,0,0.3)', padding: '2px 6px', borderRadius: '4px', color: 'var(--accent)' }} {...props}>
                              {children}
                            </code>
                          )
                        }
                      }}
                    >
                      {msg.content}
                    </ReactMarkdown>
                    {isLoading && idx === messages.length - 1 && msg.content === '' && (
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-muted)' }}>
                        <Loader2 size={16} className="spin" style={{ animation: 'spin 1s linear infinite' }} /> Thinking...
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      <div style={{ padding: '24px', borderTop: '1px solid var(--border)', background: 'var(--bg-secondary)' }}>
        <div className="glass-card" style={{ display: 'flex', alignItems: 'flex-end', padding: '12px', borderRadius: '16px', background: 'var(--bg-input)' }}>
          <textarea
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about your codebase..."
            style={{
              flex: 1,
              background: 'transparent',
              border: 'none',
              color: '#fff',
              outline: 'none',
              resize: 'none',
              padding: '8px',
              fontFamily: 'inherit',
              fontSize: '15px',
              minHeight: '24px',
              maxHeight: '200px'
            }}
            rows={1}
          />
          <button 
            className="btn-primary" 
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            style={{ padding: '10px', borderRadius: '12px', marginLeft: '12px' }}
          >
            <Send size={18} />
          </button>
        </div>
        <div style={{ textAlign: 'center', marginTop: '12px', fontSize: '12px', color: 'var(--text-muted)' }}>
          Press Enter to send, Shift+Enter for new line
        </div>
      </div>
    </div>
  );
}
