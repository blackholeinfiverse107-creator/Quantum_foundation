import React from 'react';

interface CrowdLevelBadgeProps {
  level: 'low' | 'medium' | 'high' | 'critical';
  showLabel?: boolean;
  size?: 'sm' | 'md' | 'lg';
}

export function CrowdLevelBadge({ level, showLabel = true, size = 'md' }: CrowdLevelBadgeProps) {
  const config = {
    low: {
      color: 'bg-[#34C759]',
      text: 'text-[#34C759]',
      label: 'Low',
    },
    medium: {
      color: 'bg-[#FFB300]',
      text: 'text-[#FFB300]',
      label: 'Medium',
    },
    high: {
      color: 'bg-[#FF9500]',
      text: 'text-[#FF9500]',
      label: 'High',
    },
    critical: {
      color: 'bg-[#FF5757]',
      text: 'text-[#FF5757]',
      label: 'Critical',
    },
  };

  const sizeClasses = {
    sm: 'text-xs px-2 py-1',
    md: 'text-sm px-3 py-1',
    lg: 'text-base px-4 py-2',
  };

  const { color, text, label } = config[level];

  if (!showLabel) {
    return <div className={`w-3 h-3 rounded-full ${color}`} />;
  }

  return (
    <div className={`inline-flex items-center gap-1.5 ${sizeClasses[size]} bg-opacity-10 ${color} rounded-full`}>
      <div className={`w-2 h-2 rounded-full ${color}`} />
      <span className={text}>{label}</span>
    </div>
  );
}
