import React from 'react';
import { Heart, AlertTriangle, Users, Camera } from 'lucide-react';
import { Card, CardHeader, CardContent } from '../Card';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

const emotionData = [
  { name: 'Neutral', value: 52, color: '#6B7280' },
  { name: 'Happy', value: 28, color: '#34C759' },
  { name: 'Stressed', value: 15, color: '#FFB300' },
  { name: 'Angry', value: 5, color: '#FF5757' },
];

const crowdDensityData = [
  { route: 'Route 15', density: 92, stress: 78 },
  { route: 'Route 42', density: 88, stress: 72 },
  { route: 'Route 8', density: 65, stress: 45 },
  { route: 'Route 23', density: 78, stress: 58 },
  { route: 'Route 7', density: 82, stress: 65 },
];

const alertsList = [
  {
    id: '1',
    type: 'overcrowding',
    bus: 'B102',
    route: 'Route 15',
    severity: 'high',
    message: 'Critical overcrowding detected',
    time: '3 min ago',
  },
  {
    id: '2',
    type: 'anomaly',
    bus: 'B104',
    route: 'Route 42',
    severity: 'medium',
    message: 'Unusual activity pattern detected',
    time: '12 min ago',
  },
  {
    id: '3',
    type: 'stress',
    bus: 'B089',
    route: 'Route 8',
    severity: 'medium',
    message: 'Elevated stress levels in passengers',
    time: '18 min ago',
  },
];

const highStressBuses = [
  { bus: 'B102', route: 'Route 15', score: 85, occupancy: 98 },
  { bus: 'B104', route: 'Route 42', score: 78, occupancy: 92 },
  { bus: 'B089', route: 'Route 8', score: 72, occupancy: 88 },
  { bus: 'B045', route: 'Route 23', score: 68, occupancy: 85 },
];

export function EmotionSafety() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-gray-900">Passenger Emotion & Safety Analytics</h2>
          <p className="text-sm text-gray-500 mt-1">
            Computer Vision-powered mood and safety monitoring
          </p>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-2 px-4 py-2 bg-green-50 rounded-xl">
            <Camera className="w-4 h-4 text-green-600" />
            <span className="text-sm text-green-900">42 Cameras Active</span>
          </div>
        </div>
      </div>

      {/* Top Row - Emotion Distribution and Stress Heatmap */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Emotion Distribution */}
        <Card>
          <CardHeader>
            <h3 className="text-gray-900">Emotion Distribution</h3>
            <p className="text-sm text-gray-500 mt-1">Current passenger mood across all routes</p>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-center">
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={emotionData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={100}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {emotionData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="grid grid-cols-4 gap-2 mt-4">
              {emotionData.map((emotion) => (
                <div key={emotion.name} className="text-center p-2 bg-gray-50 rounded-lg">
                  <div className="w-3 h-3 rounded-full mx-auto mb-1" style={{ backgroundColor: emotion.color }} />
                  <div className="text-xs text-gray-600">{emotion.name}</div>
                  <div className="text-sm text-gray-900">{emotion.value}%</div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Stress Heatmap */}
        <Card>
          <CardHeader>
            <h3 className="text-gray-900">Live Stress Heatmap</h3>
            <p className="text-sm text-gray-500 mt-1">Stress levels per route</p>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={crowdDensityData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                <XAxis dataKey="route" stroke="#6B7280" />
                <YAxis stroke="#6B7280" />
                <Tooltip />
                <Legend />
                <Bar dataKey="density" fill="#1A73E8" radius={[8, 8, 0, 0]} name="Crowd Density %" />
                <Bar dataKey="stress" fill="#FFB300" radius={[8, 8, 0, 0]} name="Stress Score" />
              </BarChart>
            </ResponsiveContainer>
            <div className="mt-4 p-3 bg-amber-50 border border-amber-200 rounded-lg">
              <div className="flex items-start gap-2">
                <AlertTriangle className="w-4 h-4 text-amber-600 mt-0.5" />
                <div className="text-xs text-amber-900">
                  <span className="font-semibold">Alert:</span> Route 15 showing high correlation between crowd
                  density and passenger stress levels.
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Crowd Density Alert Cards */}
      <Card>
        <CardHeader>
          <h3 className="text-gray-900">Active Safety Alerts</h3>
          <p className="text-sm text-gray-500 mt-1">Real-time alerts from CV systems</p>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {alertsList.map((alert) => (
              <div
                key={alert.id}
                className={`p-4 rounded-xl border-2 ${
                  alert.severity === 'high'
                    ? 'bg-red-50 border-red-200'
                    : 'bg-amber-50 border-amber-200'
                }`}
              >
                <div className="flex items-start justify-between mb-2">
                  <div
                    className={`p-2 rounded-lg ${
                      alert.severity === 'high' ? 'bg-red-200' : 'bg-amber-200'
                    }`}
                  >
                    <AlertTriangle
                      className={`w-4 h-4 ${
                        alert.severity === 'high' ? 'text-red-700' : 'text-amber-700'
                      }`}
                    />
                  </div>
                  <span className="text-xs text-gray-500">{alert.time}</span>
                </div>
                <div className="text-sm text-gray-900 mb-1">{alert.message}</div>
                <div className="text-xs text-gray-600">
                  {alert.bus} • {alert.route}
                </div>
                <button className="mt-3 w-full px-3 py-2 bg-white text-gray-900 rounded-lg text-xs hover:shadow transition-shadow">
                  View Camera Feed
                </button>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* High Stress Buses List */}
      <Card>
        <CardHeader>
          <h3 className="text-gray-900">Buses with Highest Stress Levels</h3>
          <p className="text-sm text-gray-500 mt-1">Requires immediate attention</p>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {highStressBuses.map((bus, index) => (
              <div
                key={bus.bus}
                className="flex items-center gap-4 p-4 bg-gradient-to-r from-red-50 to-amber-50 rounded-xl hover:shadow-md transition-all cursor-pointer"
              >
                <div className="flex items-center justify-center w-10 h-10 bg-gradient-to-br from-red-500 to-amber-500 text-white rounded-lg">
                  {index + 1}
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-gray-900">{bus.bus}</span>
                    <span className="text-sm text-gray-500">•</span>
                    <span className="text-sm text-gray-600">{bus.route}</span>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="flex-1">
                      <div className="flex items-center justify-between text-xs text-gray-600 mb-1">
                        <span>Stress Score</span>
                        <span className="text-gray-900">{bus.score}/100</span>
                      </div>
                      <div className="w-full bg-white rounded-full h-2">
                        <div
                          className="bg-gradient-to-r from-amber-500 to-red-500 h-2 rounded-full"
                          style={{ width: `${bus.score}%` }}
                        />
                      </div>
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between text-xs text-gray-600 mb-1">
                        <span>Occupancy</span>
                        <span className="text-gray-900">{bus.occupancy}%</span>
                      </div>
                      <div className="w-full bg-white rounded-full h-2">
                        <div
                          className="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full"
                          style={{ width: `${bus.occupancy}%` }}
                        />
                      </div>
                    </div>
                  </div>
                </div>
                <button className="px-4 py-2 bg-white text-gray-900 rounded-lg text-sm hover:shadow transition-shadow">
                  Dispatch Support
                </button>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
