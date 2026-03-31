import React from 'react';
import {
  LayoutDashboard,
  Lightbulb,
  TrendingUp,
  Heart,
  Users,
  Wrench,
  Shield,
  Leaf,
} from 'lucide-react';

interface OperatorSidebarProps {
  activePage: string;
  onPageChange: (page: string) => void;
}

export function OperatorSidebar({ activePage, onPageChange }: OperatorSidebarProps) {
  const menuItems = [
    { id: 'overview', label: 'Mission Control', icon: LayoutDashboard },
    { id: 'rl-recommendations', label: 'RL Recommendations', icon: Lightbulb },
    { id: 'demand-forecast', label: 'Demand & Crowd', icon: TrendingUp },
    { id: 'emotion-safety', label: 'Emotion & Safety', icon: Heart },
    { id: 'driver-behavior', label: 'Driver Analytics', icon: Users },
    { id: 'maintenance', label: 'Predictive Maintenance', icon: Wrench },
    { id: 'fraud', label: 'Fraud Detection', icon: Shield },
    { id: 'sustainability', label: 'Sustainability', icon: Leaf },
  ];

  return (
    <div className="w-72 bg-white border-r border-gray-200 h-[calc(100vh-73px)] sticky top-[73px] overflow-y-auto">
      <div className="p-4">
        <div className="text-xs text-gray-500 mb-3 px-3">CONTROL CENTER</div>
        <nav className="space-y-1">
          {menuItems.map((item) => {
            const Icon = item.icon;
            return (
              <button
                key={item.id}
                onClick={() => onPageChange(item.id)}
                className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all ${
                  activePage === item.id
                    ? 'bg-gradient-to-r from-[#1A73E8] to-[#34C759] text-white shadow-md'
                    : 'text-gray-600 hover:bg-gray-50'
                }`}
              >
                <Icon className="w-5 h-5" />
                <span className="text-sm">{item.label}</span>
              </button>
            );
          })}
        </nav>
      </div>
    </div>
  );
}
