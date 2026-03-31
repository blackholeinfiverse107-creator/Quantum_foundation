import React, { useState } from 'react';
import { Lightbulb, TrendingDown, Clock, Leaf, CheckCircle, X } from 'lucide-react';
import { Card, CardHeader, CardContent } from '../Card';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

interface Recommendation {
  id: string;
  routeId: string;
  action: string;
  reason: string;
  impact: {
    overcrowding: number;
    waitingTime: number;
    co2: number;
  };
  confidence: number;
}

const mockRecommendations: Recommendation[] = [
  {
    id: '1',
    routeId: 'Route 15',
    action: 'Increase Frequency by 2 buses',
    reason: 'High demand detected during peak hours',
    impact: { overcrowding: -35, waitingTime: -28, co2: 8 },
    confidence: 92,
  },
  {
    id: '2',
    routeId: 'Route 42',
    action: 'Add Express Shuttle',
    reason: 'Major event detected at Tech Park',
    impact: { overcrowding: -45, waitingTime: -40, co2: 5 },
    confidence: 88,
  },
  {
    id: '3',
    routeId: 'Route 8',
    action: 'Reduce Frequency by 1 bus',
    reason: 'Low demand period, optimize resources',
    impact: { overcrowding: 5, waitingTime: 8, co2: -25 },
    confidence: 85,
  },
  {
    id: '4',
    routeId: 'Route 23',
    action: 'Reroute via Main Street',
    reason: 'Construction causing delays on Oak Avenue',
    impact: { overcrowding: -10, waitingTime: -22, co2: -5 },
    confidence: 90,
  },
];

const simulationData = [
  { time: '8:00', before: 12, after: 8 },
  { time: '8:30', before: 15, after: 9 },
  { time: '9:00', before: 18, after: 10 },
  { time: '9:30', before: 14, after: 8 },
  { time: '10:00', before: 11, after: 7 },
  { time: '10:30', before: 13, after: 8 },
];

export function RLRecommendations() {
  const [selectedRec, setSelectedRec] = useState<string | null>(null);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-gray-900">AI Recommendations Center</h2>
          <p className="text-sm text-gray-500 mt-1">
            Reinforcement Learning-powered optimization suggestions
          </p>
        </div>
        <div className="flex items-center gap-3">
          <div className="text-sm text-gray-600">
            Last updated: <span className="text-gray-900">2 minutes ago</span>
          </div>
          <button className="px-4 py-2 bg-gradient-to-r from-[#1A73E8] to-[#34C759] text-white rounded-xl hover:shadow-lg transition-all">
            Refresh Recommendations
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recommendations List */}
        <div className="space-y-4">
          {mockRecommendations.map((rec) => (
            <Card
              key={rec.id}
              hover
              onClick={() => setSelectedRec(rec.id)}
              className={selectedRec === rec.id ? 'ring-2 ring-[#1A73E8]' : ''}
            >
              <CardContent className="p-5">
                <div className="flex items-start gap-4">
                  <div className="p-3 bg-gradient-to-br from-[#1A73E8] to-[#34C759] rounded-xl">
                    <Lightbulb className="w-6 h-6 text-white" />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-start justify-between mb-2">
                      <div>
                        <div className="text-sm text-[#1A73E8] mb-1">{rec.routeId}</div>
                        <h4 className="text-gray-900">{rec.action}</h4>
                        <p className="text-sm text-gray-500 mt-1">{rec.reason}</p>
                      </div>
                      <div className="text-right">
                        <div className="text-sm text-gray-900">{rec.confidence}%</div>
                        <div className="text-xs text-gray-500">Confidence</div>
                      </div>
                    </div>

                    {/* Impact Metrics */}
                    <div className="flex gap-3 mt-4 mb-4">
                      <div className="flex-1 bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-3">
                        <div className="flex items-center gap-1 text-xs text-green-700 mb-1">
                          <TrendingDown className="w-3 h-3" />
                          <span>Overcrowding</span>
                        </div>
                        <div className="text-lg text-green-900">{rec.impact.overcrowding}%</div>
                      </div>
                      <div className="flex-1 bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-3">
                        <div className="flex items-center gap-1 text-xs text-blue-700 mb-1">
                          <Clock className="w-3 h-3" />
                          <span>Wait Time</span>
                        </div>
                        <div className="text-lg text-blue-900">{rec.impact.waitingTime}%</div>
                      </div>
                      <div className="flex-1 bg-gradient-to-br from-emerald-50 to-emerald-100 rounded-lg p-3">
                        <div className="flex items-center gap-1 text-xs text-emerald-700 mb-1">
                          <Leaf className="w-3 h-3" />
                          <span>CO₂</span>
                        </div>
                        <div className="text-lg text-emerald-900">{rec.impact.co2}%</div>
                      </div>
                    </div>

                    {/* Action Buttons */}
                    <div className="flex gap-2">
                      <button className="flex-1 px-4 py-2 bg-[#34C759] text-white rounded-lg hover:bg-[#2ba848] transition-colors flex items-center justify-center gap-2">
                        <CheckCircle className="w-4 h-4" />
                        <span className="text-sm">Approve</span>
                      </button>
                      <button className="flex-1 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors flex items-center justify-center gap-2">
                        <span className="text-sm">Modify</span>
                      </button>
                      <button className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors">
                        <X className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Simulation View */}
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <h3 className="text-gray-900">Impact Simulation</h3>
              <p className="text-sm text-gray-500 mt-1">Before vs After comparison</p>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={simulationData}>
                  <defs>
                    <linearGradient id="colorBefore" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#FF5757" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#FF5757" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="colorAfter" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#34C759" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#34C759" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                  <XAxis dataKey="time" stroke="#6B7280" />
                  <YAxis stroke="#6B7280" label={{ value: 'Wait Time (min)', angle: -90, position: 'insideLeft' }} />
                  <Tooltip />
                  <Legend />
                  <Area
                    type="monotone"
                    dataKey="before"
                    stroke="#FF5757"
                    fillOpacity={1}
                    fill="url(#colorBefore)"
                    name="Before"
                  />
                  <Area
                    type="monotone"
                    dataKey="after"
                    stroke="#34C759"
                    fillOpacity={1}
                    fill="url(#colorAfter)"
                    name="After"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-5">
              <h4 className="text-gray-900 mb-4">Expected Outcomes</h4>
              <div className="space-y-3">
                <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                  <span className="text-sm text-gray-700">Passenger Satisfaction</span>
                  <span className="text-sm text-green-700">↑ 24%</span>
                </div>
                <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                  <span className="text-sm text-gray-700">Service Efficiency</span>
                  <span className="text-sm text-blue-700">↑ 18%</span>
                </div>
                <div className="flex items-center justify-between p-3 bg-purple-50 rounded-lg">
                  <span className="text-sm text-gray-700">Cost Savings</span>
                  <span className="text-sm text-purple-700">$1,250/day</span>
                </div>
                <div className="flex items-center justify-between p-3 bg-emerald-50 rounded-lg">
                  <span className="text-sm text-gray-700">Carbon Reduction</span>
                  <span className="text-sm text-emerald-700">↓ 340 kg/day</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
