import React from 'react';

export default function SeverityBadge({ status }) {
  const s = (status || 'unknown').toLowerCase();

  if (s === 'critical') return <span className="badge critical">🚨 Critical</span>;
  if (s === 'warning')  return <span className="badge warning">⚠ Warning</span>;
  if (s === 'normal')   return <span className="badge normal">✓ Normal</span>;
  return <span className="badge unknown">? Unknown</span>;
}
