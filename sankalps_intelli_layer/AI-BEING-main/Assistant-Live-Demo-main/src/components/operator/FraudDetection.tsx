import React from 'react';
import { Shield, AlertTriangle, TrendingUp } from 'lucide-react';
import { Card, CardHeader, CardContent } from '../Card';
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const fraudTrend = [
  { date: 'Mon', incidents: 12 },
  { date: 'Tue', incidents: 15 },
  { date: 'Wed', incidents: 8 },
  { date: 'Thu', incidents: 18 },
  { date: 'Fri', incidents: 22 },
  { date: 'Sat', incidents: 10 },
  { date: 'Sun', incidents: 6 },
];

const routeFraud = [
  { route: 'Route 15', incidents: 34 },
  { route: 'Route 42', incidents: 28 },
  { route: 'Route 8', incidents: 19 },
  { route: 'Route 23', incidents: 15 },
  { route: 'Route 7', incidents: 12 },
];

export function FraudDetection() {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-gray-900">Ticketing Fraud & Anomaly Detection</h2>
        <p className="text-sm text-gray-500 mt-1">AI-powered fraud pattern recognition</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="border-l-4 border-red-500">
          <CardContent className="p-5">
            <div className="flex items-center justify-between mb-2">
              <Shield className="w-8 h-8 text-red-600" />
              <span className="text-2xl text-red-900">91</span>
            </div>
            <div className="text-sm text-gray-600">Fraud Incidents (Week)</div>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-amber-500">
          <CardContent className="p-5">
            <div className="flex items-center justify-between mb-2">
              <AlertTriangle className="w-8 h-8 text-amber-600" />
              <span className="text-2xl text-amber-900">34</span>
            </div>
            <div className="text-sm text-gray-600">Pass Misuse</div>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-purple-500">
          <CardContent className="p-5">
            <div className="flex items-center justify-between mb-2">
              <TrendingUp className="w-8 h-8 text-purple-600" />
              <span className="text-2xl text-purple-900">$2,340</span>
            </div>
            <div className="text-sm text-gray-600">Revenue Loss</div>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-green-500">
          <CardContent className="p-5">
            <div className="flex items-center justify-between mb-2">
              <Shield className="w-8 h-8 text-green-600" />
              <span className="text-2xl text-green-900">78%</span>
            </div>
            <div className="text-sm text-gray-600">Detection Rate</div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Fraud Trend */}
        <Card>
          <CardHeader>
            <h3 className="text-gray-900">Weekly Fraud Trend</h3>
            <p className="text-sm text-gray-500 mt-1">Incidents detected per day</p>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={fraudTrend}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                <XAxis dataKey="date" stroke="#6B7280" />
                <YAxis stroke="#6B7280" />
                <Tooltip />
                <Line
                  type="monotone"
                  dataKey="incidents"
                  stroke="#FF5757"
                  strokeWidth={3}
                  dot={{ r: 5, fill: '#FF5757' }}
                />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Route-based Fraud */}
        <Card>
          <CardHeader>
            <h3 className="text-gray-900">Route-Based Fraud Heatmap</h3>
            <p className="text-sm text-gray-500 mt-1">Incidents by route</p>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={routeFraud}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                <XAxis dataKey="route" stroke="#6B7280" />
                <YAxis stroke="#6B7280" />
                <Tooltip />
                <Bar dataKey="incidents" fill="#FF5757" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Suspicious Activities */}
      <Card>
        <CardHeader>
          <h3 className="text-gray-900">Recent Suspicious Activities</h3>
          <p className="text-sm text-gray-500 mt-1">Flagged for review</p>
        </CardHeader>
        <CardContent className="space-y-3">
          {[
            {
              type: 'Invalid QR Code',
              route: 'Route 15',
              time: '15 min ago',
              severity: 'high',
              details: 'Same QR scanned 12 times in 2 hours',
            },
            {
              type: 'Expired Pass',
              route: 'Route 42',
              time: '45 min ago',
              severity: 'medium',
              details: 'Pass expired 3 days ago, used multiple times',
            },
            {
              type: 'Conductor Anomaly',
              route: 'Route 8',
              time: '2 hours ago',
              severity: 'high',
              details: 'Unusual ticket pattern detected',
            },
            {
              type: 'Student Pass Misuse',
              route: 'Route 23',
              time: '3 hours ago',
              severity: 'low',
              details: 'Student pass used during non-peak hours',
            },
          ].map((activity, idx) => (
            <div
              key={idx}
              className={`p-4 rounded-xl border ${
                activity.severity === 'high'
                  ? 'bg-red-50 border-red-200'
                  : activity.severity === 'medium'
                  ? 'bg-amber-50 border-amber-200'
                  : 'bg-blue-50 border-blue-200'
              }`}
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-2">
                  <AlertTriangle
                    className={`w-4 h-4 ${
                      activity.severity === 'high'
                        ? 'text-red-600'
                        : activity.severity === 'medium'
                        ? 'text-amber-600'
                        : 'text-blue-600'
                    }`}
                  />
                  <span className="text-sm text-gray-900">{activity.type}</span>
                </div>
                <span className="text-xs text-gray-500">{activity.time}</span>
              </div>
              <div className="text-xs text-gray-600 mb-2">{activity.route}</div>
              <div className="text-xs text-gray-700 bg-white px-3 py-2 rounded-lg mb-3">{activity.details}</div>
              <div className="flex gap-2">
                <button className="flex-1 px-3 py-2 bg-white text-gray-900 rounded-lg text-xs hover:shadow transition-shadow">
                  Review Details
                </button>
                <button className="px-3 py-2 bg-white text-gray-900 rounded-lg text-xs hover:shadow transition-shadow">
                  Flag
                </button>
                <button className="px-3 py-2 bg-white text-gray-900 rounded-lg text-xs hover:shadow transition-shadow">
                  Dismiss
                </button>
              </div>
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Conductor Risk Ranking */}
      <Card>
        <CardHeader>
          <h3 className="text-gray-900">Conductor Fraud Risk Ranking</h3>
          <p className="text-sm text-gray-500 mt-1">Patterns requiring investigation</p>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {[
              { id: 'C-234', name: 'Conductor A', risk: 85, anomalies: 12 },
              { id: 'C-156', name: 'Conductor B', risk: 72, anomalies: 8 },
              { id: 'C-089', name: 'Conductor C', risk: 58, anomalies: 5 },
              { id: 'C-445', name: 'Conductor D', risk: 42, anomalies: 3 },
            ].map((conductor) => (
              <div
                key={conductor.id}
                className="flex items-center gap-4 p-4 bg-gradient-to-r from-gray-50 to-white rounded-xl hover:shadow-md transition-all cursor-pointer"
              >
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-gray-900">{conductor.name}</span>
                    <span className="text-xs text-gray-500">({conductor.id})</span>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="flex-1">
                      <div className="flex items-center justify-between text-xs text-gray-600 mb-1">
                        <span>Risk Score</span>
                        <span className="text-gray-900">{conductor.risk}/100</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full ${
                            conductor.risk > 70
                              ? 'bg-red-500'
                              : conductor.risk > 50
                              ? 'bg-amber-500'
                              : 'bg-green-500'
                          }`}
                          style={{ width: `${conductor.risk}%` }}
                        />
                      </div>
                    </div>
                  </div>
                </div>
                <div className="text-center">
                  <div className="text-xl text-gray-900">{conductor.anomalies}</div>
                  <div className="text-xs text-gray-500">Anomalies</div>
                </div>
                <button className="px-4 py-2 bg-red-100 text-red-700 rounded-lg text-sm hover:bg-red-200 transition-colors">
                  Investigate
                </button>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
