import React from 'react';
import { LayoutDashboard, Smartphone, Truck } from 'lucide-react';

interface NavigationProps {
  currentView: 'operator' | 'passenger' | 'driver';
  onViewChange: (view: 'operator' | 'passenger' | 'driver') => void;
}

export function Navigation({ currentView, onViewChange }: NavigationProps) {
  const views = [
    { id: 'operator' as const, label: 'Operator Dashboard', icon: LayoutDashboard },
    { id: 'passenger' as const, label: 'Passenger App', icon: Smartphone },
    { id: 'driver' as const, label: 'Driver App', icon: Truck },
  ];

  return (
    <div className="bg-white border-b border-gray-200 shadow-sm sticky top-0 z-50">
      <div className="max-w-[1800px] mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-[#1A73E8] to-[#34C759] rounded-xl flex items-center justify-center">
              <LayoutDashboard className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl text-gray-900">Smart Transit Control</h1>
              <p className="text-xs text-gray-500">AI-Powered Transport Platform</p>
            </div>
          </div>

          <div className="flex gap-2 bg-gray-100 p-1 rounded-xl">
            {views.map((view) => {
              const Icon = view.icon;
              return (
                <button
                  key={view.id}
                  onClick={() => onViewChange(view.id)}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${
                    currentView === view.id
                      ? 'bg-white shadow-sm text-[#1A73E8]'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span className="text-sm">{view.label}</span>
                </button>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
