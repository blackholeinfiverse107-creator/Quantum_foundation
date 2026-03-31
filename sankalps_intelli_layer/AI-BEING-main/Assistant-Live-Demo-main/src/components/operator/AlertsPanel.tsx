import React from 'react';
import { AlertTriangle, Bus, User, Flame, MapPin } from 'lucide-react';
import { Card, CardHeader, CardContent } from '../Card';

interface Alert {
  id: string;
  type: 'route' | 'driver' | 'fraud' | 'mechanical';
  severity: 'high' | 'medium' | 'low';
  title: string;
  description: string;
  time: string;
}

const mockAlerts: Alert[] = [
  {
    id: '1',
    type: 'driver',
    severity: 'high',
    title: 'Drowsiness Alert - Driver D-458',
    description: 'Bus B102 on Route 15',
    time: '2 min ago',
  },
  {
    id: '2',
    type: 'route',
    severity: 'medium',
    title: 'Route Deviation Detected',
    description: 'Bus B104 diverted from Route 42',
    time: '5 min ago',
  },
  {
    id: '3',
    type: 'mechanical',
    severity: 'high',
    title: 'Engine Temperature Critical',
    description: 'Bus B107 - Temperature 105°C',
    time: '8 min ago',
  },
  {
    id: '4',
    type: 'fraud',
    severity: 'medium',
    title: 'Suspicious Ticket Pattern',
    description: 'Route 23 - Multiple invalid passes',
    time: '15 min ago',
  },
];

export function AlertsPanel() {
  const getIcon = (type: Alert['type']) => {
    switch (type) {
      case 'driver':
        return User;
      case 'route':
        return MapPin;
      case 'mechanical':
        return Flame;
      case 'fraud':
        return AlertTriangle;
    }
  };

  const getSeverityColor = (severity: Alert['severity']) => {
    switch (severity) {
      case 'high':
        return 'bg-red-100 text-red-700 border-red-200';
      case 'medium':
        return 'bg-amber-100 text-amber-700 border-amber-200';
      case 'low':
        return 'bg-blue-100 text-blue-700 border-blue-200';
    }
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-gray-900">Live Alerts</h3>
            <p className="text-sm text-gray-500 mt-1">Priority incidents requiring attention</p>
          </div>
          <div className="bg-red-100 text-red-700 px-3 py-1 rounded-full text-sm">
            {mockAlerts.length} Active
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-2 max-h-[400px] overflow-y-auto">
        {mockAlerts.map((alert) => {
          const Icon = getIcon(alert.type);
          return (
            <div
              key={alert.id}
              className={`p-3 rounded-xl border ${getSeverityColor(
                alert.severity
              )} hover:shadow-md transition-all cursor-pointer`}
            >
              <div className="flex items-start gap-3">
                <div
                  className={`p-2 rounded-lg ${
                    alert.severity === 'high'
                      ? 'bg-red-200'
                      : alert.severity === 'medium'
                      ? 'bg-amber-200'
                      : 'bg-blue-200'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between gap-2">
                    <div className="text-sm">{alert.title}</div>
                    <div className="text-xs whitespace-nowrap">{alert.time}</div>
                  </div>
                  <div className="text-xs opacity-80 mt-1">{alert.description}</div>
                  <div className="flex gap-2 mt-2">
                    <button className="text-xs px-3 py-1 bg-white rounded-lg hover:shadow transition-shadow">
                      View Details
                    </button>
                    <button className="text-xs px-3 py-1 bg-white rounded-lg hover:shadow transition-shadow">
                      Dismiss
                    </button>
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </CardContent>
    </Card>
  );
}
