import React, { useEffect, useState } from 'react';

export default function HealthScore({ score = 0, label = 'Health Score' }) {
  const [currentScore, setCurrentScore] = useState(0);
  
  useEffect(() => {
    const timer = setTimeout(() => {
      setCurrentScore(score);
    }, 100);
    return () => clearTimeout(timer);
  }, [score]);

  const getColor = (val) => {
    if (val < 40) return '#ef4444'; // red
    if (val < 70) return '#eab308'; // yellow
    return '#22c55e'; // green
  };

  const color = getColor(currentScore);
  const radius = 36;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (currentScore / 100) * circumference;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
      <div style={{ position: 'relative', width: '96px', height: '96px' }}>
        <svg width="96" height="96" style={{ transform: 'rotate(-90deg)' }}>
          <circle
            cx="48" cy="48" r={radius}
            fill="transparent"
            stroke="var(--bg-input)"
            strokeWidth="8"
          />
          <circle
            cx="48" cy="48" r={radius}
            fill="transparent"
            stroke={color}
            strokeWidth="8"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            style={{ transition: 'stroke-dashoffset 1s ease-out, stroke 1s ease-out' }}
          />
        </svg>
        <div style={{
          position: 'absolute', top: 0, left: 0, right: 0, bottom: 0,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: '24px', fontWeight: 700, color: 'var(--text-primary)'
        }}>
          {Math.round(currentScore)}
        </div>
      </div>
      <div style={{ marginTop: '8px', fontSize: '14px', color: 'var(--text-secondary)', fontWeight: 500 }}>
        {label}
      </div>
    </div>
  );
}
