import React from 'react';

interface GlowingIndicatorProps {
  status: 'online' | 'warning' | 'error' | 'offline';
  size?: 'sm' | 'md' | 'lg';
  label?: string;
}

export function GlowingIndicator({ status, size = 'md', label }: GlowingIndicatorProps) {
  const sizeClasses = {
    sm: 'w-2 h-2',
    md: 'w-3 h-3',
    lg: 'w-4 h-4',
  };

  const statusColors = {
    online: 'bg-[#34C759]',
    warning: 'bg-[#FFB300]',
    error: 'bg-[#FF5757]',
    offline: 'bg-gray-400',
  };

  const glowColors = {
    online: 'shadow-[0_0_10px_rgba(52,199,89,0.5)]',
    warning: 'shadow-[0_0_10px_rgba(255,179,0,0.5)]',
    error: 'shadow-[0_0_10px_rgba(255,87,87,0.5)]',
    offline: 'shadow-[0_0_10px_rgba(156,163,175,0.3)]',
  };

  return (
    <div className="flex items-center gap-2">
      <div
        className={`${sizeClasses[size]} ${statusColors[status]} ${glowColors[status]} rounded-full pulse-glow`}
      />
      {label && <span className="text-sm text-gray-600">{label}</span>}
    </div>
  );
}
