import React from 'react';
import { Clock, Users, AlertCircle, Leaf, TrendingUp, TrendingDown } from 'lucide-react';
import { Card, CardContent } from '../Card';

interface KPI {
  label: string;
  value: string;
  change: number;
  icon: React.ElementType;
  color: string;
}

const kpis: KPI[] = [
  {
    label: 'Avg Waiting Time',
    value: '4.2 min',
    change: -12,
    icon: Clock,
    color: 'from-blue-500 to-blue-600',
  },
  {
    label: 'Avg Occupancy',
    value: '68%',
    change: 5,
    icon: Users,
    color: 'from-purple-500 to-purple-600',
  },
  {
    label: 'Delays per Route',
    value: '2.4',
    change: -8,
    icon: AlertCircle,
    color: 'from-amber-500 to-amber-600',
  },
  {
    label: 'CO₂ Emissions',
    value: '1,245 kg',
    change: -15,
    icon: Leaf,
    color: 'from-green-500 to-green-600',
  },
  {
    label: 'Bus Utilization',
    value: '89%',
    change: 3,
    icon: TrendingUp,
    color: 'from-indigo-500 to-indigo-600',
  },
];

export function KPICards() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
      {kpis.map((kpi) => {
        const Icon = kpi.icon;
        const isPositive = kpi.change < 0; // For metrics where lower is better

        return (
          <Card key={kpi.label} className="hover:shadow-lg transition-all">
            <CardContent className="p-5">
              <div className="flex items-start justify-between mb-3">
                <div className={`p-3 rounded-xl bg-gradient-to-br ${kpi.color}`}>
                  <Icon className="w-5 h-5 text-white" />
                </div>
                <div
                  className={`flex items-center gap-1 text-xs px-2 py-1 rounded-full ${
                    isPositive ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                  }`}
                >
                  {isPositive ? (
                    <TrendingDown className="w-3 h-3" />
                  ) : (
                    <TrendingUp className="w-3 h-3" />
                  )}
                  <span>{Math.abs(kpi.change)}%</span>
                </div>
              </div>
              <div className="text-2xl text-gray-900 mb-1">{kpi.value}</div>
              <div className="text-xs text-gray-500">{kpi.label}</div>
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
}
