/**
 * SeverityBadge Component
 * 
 * =============================================================================
 * CATEGORY B: HUMAN IMPLEMENTATION REQUIRED
 * =============================================================================
 * Renders clinical severity indicators for each lab result.
 * 
 * SEVERITY BADGE SPECIFICATIONS:
 * - Normal:   "✓ NORMAL"   (Green palette)
 * - Warning:  "⚠ WARNING"  (Amber/Yellow palette)
 * - Critical: "🚨 CRITICAL" (Red palette)
 * - Unknown:  "? UNKNOWN"  (Slate/Gray palette)
 * =============================================================================
 */

import React from 'react';
import { CheckCircle2, AlertTriangle, AlertOctagon, HelpCircle } from 'lucide-react';

export default function SeverityBadge({ status }) {
  // ===========================================================================
  // TODO: HUMAN IMPLEMENTATION REQUIRED
  // Customize or extend severity badge formatting, icons, and color classes.
  // ===========================================================================

  const normalizedStatus = (status || 'Unknown').toLowerCase();

  switch (normalizedStatus) {
    case 'normal':
      return (
        <span className="severity-badge normal">
          <CheckCircle2 size={13} />
          ✓ NORMAL
        </span>
      );

    case 'warning':
      return (
        <span className="severity-badge warning">
          <AlertTriangle size={13} />
          ⚠ WARNING
        </span>
      );

    case 'critical':
      return (
        <span className="severity-badge critical">
          <AlertOctagon size={13} />
          🚨 CRITICAL
        </span>
      );

    default:
      return (
        <span className="severity-badge unknown">
          <HelpCircle size={13} />
          ? UNKNOWN
        </span>
      );
  }
}
