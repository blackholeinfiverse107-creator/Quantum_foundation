import React, { useState } from 'react';
import { Wrench, AlertTriangle, CheckCircle, Calendar } from 'lucide-react';
import { Card, CardHeader, CardContent } from '../Card';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const vibrationData = [
  { time: '00:00', level: 12 },
  { time: '04:00', level: 15 },
  { time: '08:00', level: 28 },
  { time: '12:00', level: 35 },
  { time: '16:00', level: 42 },
  { time: '20:00', level: 38 },
];

const busesAtRisk = [
  {
    id: 'B107',
    route: 'Route 8',
    component: 'Engine',
    probability: 85,
    maintenanceDate: '2025-12-05',
    priority: 'high',
  },
  {
    id: 'B089',
    route: 'Route 15',
    component: 'Transmission',
    probability: 72,
    maintenanceDate: '2025-12-08',
    priority: 'medium',
  },
  {
    id: 'B134',
    route: 'Route 42',
    component: 'Brake System',
    probability: 68,
    maintenanceDate: '2025-12-10',
    priority: 'medium',
  },
  {
    id: 'B045',
    route: 'Route 23',
    component: 'Air Conditioning',
    probability: 55,
    maintenanceDate: '2025-12-15',
    priority: 'low',
  },
];

export function PredictiveMaintenance() {
  const [showModal, setShowModal] = useState(false);
  const [selectedBus, setSelectedBus] = useState<string | null>(null);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-gray-900">Predictive Maintenance Center</h2>
        <p className="text-sm text-gray-500 mt-1">AI-powered failure prediction and scheduling</p>
      </div>

      {/* Fleet Health Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="border-l-4 border-green-500">
          <CardContent className="p-5">
            <div className="flex items-center justify-between mb-2">
              <CheckCircle className="w-8 h-8 text-green-600" />
              <span className="text-2xl text-green-900">28</span>
            </div>
            <div className="text-sm text-gray-600">Healthy Buses</div>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-amber-500">
          <CardContent className="p-5">
            <div className="flex items-center justify-between mb-2">
              <AlertTriangle className="w-8 h-8 text-amber-600" />
              <span className="text-2xl text-amber-900">8</span>
            </div>
            <div className="text-sm text-gray-600">Needs Attention</div>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-red-500">
          <CardContent className="p-5">
            <div className="flex items-center justify-between mb-2">
              <Wrench className="w-8 h-8 text-red-600" />
              <span className="text-2xl text-red-900">4</span>
            </div>
            <div className="text-sm text-gray-600">Critical Risk</div>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-blue-500">
          <CardContent className="p-5">
            <div className="flex items-center justify-between mb-2">
              <Calendar className="w-8 h-8 text-blue-600" />
              <span className="text-2xl text-blue-900">12</span>
            </div>
            <div className="text-sm text-gray-600">Scheduled</div>
          </CardContent>
        </Card>
      </div>

      {/* Engine Vibration Chart */}
      <Card>
        <CardHeader>
          <h3 className="text-gray-900">Engine Vibration Trends</h3>
          <p className="text-sm text-gray-500 mt-1">Average vibration levels across fleet</p>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={vibrationData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
              <XAxis dataKey="time" stroke="#6B7280" />
              <YAxis stroke="#6B7280" label={{ value: 'Vibration Level', angle: -90, position: 'insideLeft' }} />
              <Tooltip />
              <Line
                type="monotone"
                dataKey="level"
                stroke="#FF5757"
                strokeWidth={3}
                dot={{ r: 5, fill: '#FF5757' }}
              />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Buses at Risk */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-gray-900">Buses Requiring Maintenance</h3>
              <p className="text-sm text-gray-500 mt-1">Sorted by failure probability</p>
            </div>
            <button className="px-4 py-2 bg-[#1A73E8] text-white rounded-xl hover:shadow-lg transition-all">
              Export Report
            </button>
          </div>
        </CardHeader>
        <CardContent className="space-y-3">
          {busesAtRisk.map((bus) => (
            <div
              key={bus.id}
              className={`p-5 rounded-xl border-2 ${
                bus.priority === 'high'
                  ? 'bg-red-50 border-red-200'
                  : bus.priority === 'medium'
                  ? 'bg-amber-50 border-amber-200'
                  : 'bg-blue-50 border-blue-200'
              }`}
            >
              <div className="flex items-start justify-between mb-3">
                <div>
                  <div className="flex items-center gap-3 mb-2">
                    <span className="text-lg text-gray-900">{bus.id}</span>
                    <span className="text-sm text-gray-500">• {bus.route}</span>
                    <span
                      className={`text-xs px-2 py-1 rounded-full ${
                        bus.priority === 'high'
                          ? 'bg-red-200 text-red-800'
                          : bus.priority === 'medium'
                          ? 'bg-amber-200 text-amber-800'
                          : 'bg-blue-200 text-blue-800'
                      }`}
                    >
                      {bus.priority.toUpperCase()}
                    </span>
                  </div>
                  <div className="text-sm text-gray-700 mb-1">Component at Risk: {bus.component}</div>
                  <div className="text-xs text-gray-600">
                    Recommended maintenance: {new Date(bus.maintenanceDate).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-3xl text-gray-900 mb-1">{bus.probability}%</div>
                  <div className="text-xs text-gray-500">Failure Risk</div>
                </div>
              </div>

              <div className="mb-3">
                <div className="w-full bg-white rounded-full h-2">
                  <div
                    className={`h-2 rounded-full ${
                      bus.priority === 'high'
                        ? 'bg-gradient-to-r from-red-500 to-red-700'
                        : bus.priority === 'medium'
                        ? 'bg-gradient-to-r from-amber-500 to-amber-700'
                        : 'bg-gradient-to-r from-blue-500 to-blue-700'
                    }`}
                    style={{ width: `${bus.probability}%` }}
                  />
                </div>
              </div>

              <div className="flex gap-2">
                <button
                  onClick={() => {
                    setSelectedBus(bus.id);
                    setShowModal(true);
                  }}
                  className="flex-1 px-4 py-2 bg-white text-gray-900 rounded-lg hover:shadow transition-shadow"
                >
                  Schedule Maintenance
                </button>
                <button className="px-4 py-2 bg-white text-gray-900 rounded-lg hover:shadow transition-shadow">
                  View Details
                </button>
              </div>
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Schedule Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <Card className="max-w-md w-full">
            <CardHeader>
              <h3 className="text-gray-900">Schedule Maintenance</h3>
              <p className="text-sm text-gray-500 mt-1">Bus {selectedBus}</p>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-sm text-gray-700 block mb-2">Maintenance Date</label>
                <input
                  type="date"
                  className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#1A73E8]"
                />
              </div>
              <div>
                <label className="text-sm text-gray-700 block mb-2">Service Type</label>
                <select className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#1A73E8]">
                  <option>Engine Inspection</option>
                  <option>Transmission Service</option>
                  <option>Brake System</option>
                  <option>Full Service</option>
                </select>
              </div>
              <div>
                <label className="text-sm text-gray-700 block mb-2">Priority</label>
                <select className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#1A73E8]">
                  <option>High - Immediate</option>
                  <option>Medium - Within 3 days</option>
                  <option>Low - Within 1 week</option>
                </select>
              </div>
              <div className="flex gap-2 pt-2">
                <button className="flex-1 px-4 py-3 bg-gradient-to-r from-[#1A73E8] to-[#34C759] text-white rounded-xl hover:shadow-lg transition-all">
                  Confirm Schedule
                </button>
                <button
                  onClick={() => setShowModal(false)}
                  className="px-4 py-3 bg-gray-100 text-gray-700 rounded-xl hover:bg-gray-200 transition-colors"
                >
                  Cancel
                </button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
