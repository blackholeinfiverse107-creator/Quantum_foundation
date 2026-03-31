import React from 'react';
import { FleetMap } from './FleetMap';
import { SystemHealthPanel } from './SystemHealthPanel';
import { AlertsPanel } from './AlertsPanel';
import { KPICards } from './KPICards';

interface MissionControlProps {
  onBusClick?: (busId: string) => void;
}

export function MissionControl({ onBusClick }: MissionControlProps) {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-gray-900">Mission Control Center</h2>
        <p className="text-sm text-gray-500 mt-1">
          Real-time fleet monitoring and system overview
        </p>
      </div>

      {/* KPI Cards */}
      <KPICards />

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Fleet Map - Takes 2 columns */}
        <div className="lg:col-span-2">
          <FleetMap onBusClick={onBusClick} />
        </div>

        {/* Right Column */}
        <div className="space-y-6">
          <SystemHealthPanel />
          <AlertsPanel />
        </div>
      </div>
    </div>
  );
}
