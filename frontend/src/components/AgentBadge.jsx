import React from 'react';
import { Bot, Shield, Cpu, Zap, Beaker, FileText, Wrench, Bug, Network } from 'lucide-react';

const agentStyles = {
  qa: { color: '#8b5cf6', icon: Bot, label: 'QA Agent' },
  security: { color: '#ef4444', icon: Shield, label: 'Security Agent' },
  architecture: { color: '#06b6d4', icon: Cpu, label: 'Architecture Agent' },
  performance: { color: '#f97316', icon: Zap, label: 'Performance Agent' },
  testing: { color: '#22c55e', icon: Beaker, label: 'Testing Agent' },
  documentation: { color: '#3b82f6', icon: FileText, label: 'Docs Agent' },
  refactoring: { color: '#eab308', icon: Wrench, label: 'Refactoring Agent' },
  bug_detection: { color: '#ec4899', icon: Bug, label: 'Bug Detection Agent' },
  dependency: { color: '#14b8a6', icon: Network, label: 'Dependency Agent' },
  default: { color: '#a78bfa', icon: Bot, label: 'Agent' }
};

export default function AgentBadge({ agent }) {
  const style = agentStyles[agent] || agentStyles.default;
  const Icon = style.icon;

  return (
    <div style={{
      display: 'inline-flex',
      alignItems: 'center',
      gap: '6px',
      padding: '4px 10px',
      background: `${style.color}15`,
      border: `1px solid ${style.color}40`,
      borderRadius: '20px',
      color: style.color,
      fontSize: '12px',
      fontWeight: 600,
      boxShadow: `0 0 10px ${style.color}20`,
      marginBottom: '8px'
    }}>
      <Icon size={14} />
      <span>{style.label}</span>
    </div>
  );
}
