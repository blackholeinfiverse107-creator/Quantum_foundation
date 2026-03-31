import React from 'react';
import { Database, Cpu, Activity, CheckCircle, AlertCircle } from 'lucide-react';
import { Card, CardHeader, CardContent } from '../Card';
import { GlowingIndicator } from '../GlowingIndicator';

interface SystemComponent {
  name: string;
  status: 'online' | 'warning' | 'error' | 'offline';
  uptime: string;
  latency?: string;
}

const systemComponents: SystemComponent[] = [
  { name: 'Kafka Streaming', status: 'online', uptime: '99.98%', latency: '12ms' },
  { name: 'API Gateway', status: 'online', uptime: '99.95%', latency: '45ms' },
  { name: 'ETA Prediction Model', status: 'online', uptime: '99.92%', latency: '120ms' },
  { name: 'Demand Forecasting', status: 'online', uptime: '99.89%', latency: '200ms' },
  { name: 'RL Agent', status: 'warning', uptime: '99.45%', latency: '350ms' },
  { name: 'Computer Vision', status: 'online', uptime: '99.78%', latency: '180ms' },
];

export function SystemHealthPanel() {
  const healthyCount = systemComponents.filter((c) => c.status === 'online').length;
  const totalCount = systemComponents.length;
  const healthPercentage = (healthyCount / totalCount) * 100;

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-gray-900">System Health</h3>
            <p className="text-sm text-gray-500 mt-1">Real-time monitoring of all services</p>
          </div>
          <div className="flex items-center gap-3">
            <div className="text-right">
              <div className="text-2xl text-gray-900">{healthPercentage.toFixed(0)}%</div>
              <div className="text-xs text-gray-500">Overall Health</div>
            </div>
            <div className="w-16 h-16 rounded-full bg-gradient-to-br from-[#34C759] to-[#1A73E8] flex items-center justify-center">
              <Activity className="w-8 h-8 text-white" />
            </div>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        {systemComponents.map((component) => (
          <div
            key={component.name}
            className="flex items-center justify-between p-3 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors"
          >
            <div className="flex items-center gap-3">
              <GlowingIndicator status={component.status} />
              <div>
                <div className="text-sm text-gray-900">{component.name}</div>
                <div className="text-xs text-gray-500">Uptime: {component.uptime}</div>
              </div>
            </div>
            {component.latency && (
              <div className="text-xs text-gray-600 bg-white px-3 py-1 rounded-full">
                {component.latency}
              </div>
            )}
          </div>
        ))}

        <div className="pt-3 mt-3 border-t border-gray-200 flex items-center justify-between">
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <CheckCircle className="w-4 h-4 text-[#34C759]" />
            <span>{healthyCount} services operational</span>
          </div>
          {totalCount - healthyCount > 0 && (
            <div className="flex items-center gap-2 text-sm text-[#FFB300]">
              <AlertCircle className="w-4 h-4" />
              <span>{totalCount - healthyCount} requiring attention</span>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
