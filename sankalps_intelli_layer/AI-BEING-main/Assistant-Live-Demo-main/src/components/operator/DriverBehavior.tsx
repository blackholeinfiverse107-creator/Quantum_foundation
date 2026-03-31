import React from 'react';
import { User, Award, AlertTriangle, TrendingUp } from 'lucide-react';
import { Card, CardHeader, CardContent } from '../Card';
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const driverScores = [
  { driver: 'D-101', name: 'John Smith', score: 95, trips: 45, alerts: 2 },
  { driver: 'D-102', name: 'Sarah Lee', score: 92, trips: 42, alerts: 3 },
  { driver: 'D-103', name: 'Mike Johnson', score: 88, trips: 38, alerts: 5 },
  { driver: 'D-104', name: 'Emma Davis', score: 85, trips: 40, alerts: 6 },
  { driver: 'D-105', name: 'Chris Wilson', score: 82, trips: 36, alerts: 8 },
];

const drowsinessData = [
  { time: '06:00', level: 10 },
  { time: '08:00', level: 15 },
  { time: '10:00', level: 25 },
  { time: '12:00', level: 35 },
  { time: '14:00', level: 45 },
  { time: '16:00', level: 30 },
];

export function DriverBehavior() {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-gray-900">Driver Behavior Analytics</h2>
        <p className="text-sm text-gray-500 mt-1">Performance monitoring and safety analysis</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Driver Leaderboard */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-gray-900">Driver Performance Leaderboard</h3>
                  <p className="text-sm text-gray-500 mt-1">Top performers this week</p>
                </div>
                <Award className="w-6 h-6 text-[#FFB300]" />
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              {driverScores.map((driver, idx) => (
                <div
                  key={driver.driver}
                  className="flex items-center gap-4 p-4 bg-gradient-to-r from-gray-50 to-white rounded-xl hover:shadow-md transition-all cursor-pointer"
                >
                  <div
                    className={`flex items-center justify-center w-10 h-10 rounded-xl text-white ${
                      idx === 0
                        ? 'bg-gradient-to-br from-yellow-400 to-yellow-600'
                        : idx === 1
                        ? 'bg-gradient-to-br from-gray-400 to-gray-500'
                        : idx === 2
                        ? 'bg-gradient-to-br from-amber-600 to-amber-700'
                        : 'bg-gray-300'
                    }`}
                  >
                    {idx + 1}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-gray-900">{driver.name}</span>
                      <span className="text-xs text-gray-500">({driver.driver})</span>
                    </div>
                    <div className="flex items-center gap-4 text-xs text-gray-600">
                      <span>{driver.trips} trips</span>
                      <span>•</span>
                      <span>{driver.alerts} alerts</span>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl text-gray-900">{driver.score}</div>
                    <div className="text-xs text-gray-500">Score</div>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </div>

        {/* Risk Score Summary */}
        <Card>
          <CardHeader>
            <h3 className="text-gray-900">Risk Analysis</h3>
            <p className="text-sm text-gray-500 mt-1">Safety metrics</p>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="p-4 bg-green-50 rounded-xl">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-green-700">Low Risk</span>
                <span className="text-xl text-green-900">12</span>
              </div>
              <div className="w-full bg-green-200 rounded-full h-2">
                <div className="bg-green-600 h-2 rounded-full" style={{ width: '60%' }} />
              </div>
            </div>

            <div className="p-4 bg-amber-50 rounded-xl">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-amber-700">Medium Risk</span>
                <span className="text-xl text-amber-900">6</span>
              </div>
              <div className="w-full bg-amber-200 rounded-full h-2">
                <div className="bg-amber-600 h-2 rounded-full" style={{ width: '30%' }} />
              </div>
            </div>

            <div className="p-4 bg-red-50 rounded-xl">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-red-700">High Risk</span>
                <span className="text-xl text-red-900">2</span>
              </div>
              <div className="w-full bg-red-200 rounded-full h-2">
                <div className="bg-red-600 h-2 rounded-full" style={{ width: '10%' }} />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Drowsiness Timeline */}
      <Card>
        <CardHeader>
          <h3 className="text-gray-900">Drowsiness Detection Timeline</h3>
          <p className="text-sm text-gray-500 mt-1">Average drowsiness levels throughout the day</p>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={drowsinessData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
              <XAxis dataKey="time" stroke="#6B7280" />
              <YAxis stroke="#6B7280" label={{ value: 'Drowsiness %', angle: -90, position: 'insideLeft' }} />
              <Tooltip />
              <Line type="monotone" dataKey="level" stroke="#FF5757" strokeWidth={3} dot={{ r: 5 }} />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Recent Alerts */}
      <Card>
        <CardHeader>
          <h3 className="text-gray-900">Recent Distraction & Safety Alerts</h3>
          <p className="text-sm text-gray-500 mt-1">Last 24 hours</p>
        </CardHeader>
        <CardContent className="space-y-2">
          {[
            {
              driver: 'D-458',
              type: 'Drowsiness',
              severity: 'high',
              time: '2 hours ago',
              action: 'Driver notified & break recommended',
            },
            {
              driver: 'D-234',
              type: 'Phone Usage',
              severity: 'medium',
              time: '4 hours ago',
              action: 'Warning issued',
            },
            {
              driver: 'D-112',
              type: 'Speeding',
              severity: 'medium',
              time: '6 hours ago',
              action: 'Speed reduced automatically',
            },
          ].map((alert, idx) => (
            <div
              key={idx}
              className={`p-4 rounded-xl border ${
                alert.severity === 'high'
                  ? 'bg-red-50 border-red-200'
                  : 'bg-amber-50 border-amber-200'
              }`}
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-2">
                  <AlertTriangle
                    className={`w-4 h-4 ${
                      alert.severity === 'high' ? 'text-red-600' : 'text-amber-600'
                    }`}
                  />
                  <span className="text-sm text-gray-900">{alert.type}</span>
                </div>
                <span className="text-xs text-gray-500">{alert.time}</span>
              </div>
              <div className="text-xs text-gray-600 mb-2">
                Driver {alert.driver}
              </div>
              <div className="text-xs text-gray-700 bg-white px-3 py-2 rounded-lg">
                Action: {alert.action}
              </div>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}
