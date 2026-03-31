import React from 'react';
import { TrendingUp, Cloud, Calendar, MapPin } from 'lucide-react';
import { Card, CardHeader, CardContent } from '../Card';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { CrowdLevelBadge } from '../CrowdLevelBadge';

const demandData = [
  { time: '06:00', demand: 120, forecast: 125, actual: 118 },
  { time: '07:00', demand: 280, forecast: 290, actual: 285 },
  { time: '08:00', demand: 450, forecast: 445, actual: 452 },
  { time: '09:00', demand: 520, forecast: 510, actual: 515 },
  { time: '10:00', demand: 380, forecast: 390, actual: 375 },
  { time: '11:00', demand: 320, forecast: 315, actual: 325 },
  { time: '12:00', demand: 400, forecast: 410, actual: 405 },
  { time: '13:00', demand: 380, forecast: 375, actual: 382 },
  { time: '14:00', demand: 350, forecast: 360, actual: 348 },
  { time: '15:00', demand: 420, forecast: 430, actual: 425 },
];

const routeDemand = [
  { route: 'Route 15', demand: 92, trend: 'up' },
  { route: 'Route 42', demand: 88, trend: 'up' },
  { route: 'Route 8', demand: 65, trend: 'down' },
  { route: 'Route 23', demand: 78, trend: 'stable' },
  { route: 'Route 7', demand: 82, trend: 'up' },
];

const stopForecast = [
  { stop: 'Central Station', crowd: 'critical', waitTime: 8, passengers: 145 },
  { stop: 'Tech Park', crowd: 'high', waitTime: 6, passengers: 98 },
  { stop: 'University Plaza', crowd: 'high', waitTime: 7, passengers: 112 },
  { stop: 'Shopping District', crowd: 'medium', waitTime: 4, passengers: 67 },
  { stop: 'Residential Square', crowd: 'low', waitTime: 2, passengers: 32 },
];

export function DemandForecasting() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-gray-900">Demand & Crowd Forecasting</h2>
          <p className="text-sm text-gray-500 mt-1">
            AI-powered predictions for demand patterns and crowd levels
          </p>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 px-4 py-2 bg-blue-50 rounded-xl">
            <Cloud className="w-4 h-4 text-blue-600" />
            <span className="text-sm text-blue-900">Sunny, 72°F</span>
          </div>
          <div className="flex items-center gap-2 px-4 py-2 bg-purple-50 rounded-xl">
            <Calendar className="w-4 h-4 text-purple-600" />
            <span className="text-sm text-purple-900">No Events Today</span>
          </div>
        </div>
      </div>

      {/* Time Series Forecast */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-gray-900">15-Minute Interval Demand Forecast</h3>
              <p className="text-sm text-gray-500 mt-1">Predicted vs Actual passenger demand</p>
            </div>
            <div className="flex gap-2">
              <button className="px-3 py-1 text-sm bg-[#1A73E8] text-white rounded-lg">Today</button>
              <button className="px-3 py-1 text-sm bg-gray-100 text-gray-600 rounded-lg hover:bg-gray-200">
                Tomorrow
              </button>
              <button className="px-3 py-1 text-sm bg-gray-100 text-gray-600 rounded-lg hover:bg-gray-200">
                Week
              </button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={350}>
            <AreaChart data={demandData}>
              <defs>
                <linearGradient id="demandGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#1A73E8" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#1A73E8" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="actualGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#34C759" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#34C759" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
              <XAxis dataKey="time" stroke="#6B7280" />
              <YAxis stroke="#6B7280" label={{ value: 'Passengers', angle: -90, position: 'insideLeft' }} />
              <Tooltip />
              <Legend />
              <Area
                type="monotone"
                dataKey="forecast"
                stroke="#1A73E8"
                fillOpacity={1}
                fill="url(#demandGradient)"
                name="Forecast"
              />
              <Area
                type="monotone"
                dataKey="actual"
                stroke="#34C759"
                fillOpacity={1}
                fill="url(#actualGradient)"
                name="Actual"
              />
            </AreaChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Route-based Demand Heatmap */}
        <Card>
          <CardHeader>
            <h3 className="text-gray-900">Route Demand Heatmap</h3>
            <p className="text-sm text-gray-500 mt-1">Current demand levels by route</p>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={routeDemand} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                <XAxis type="number" stroke="#6B7280" />
                <YAxis dataKey="route" type="category" stroke="#6B7280" />
                <Tooltip />
                <Bar
                  dataKey="demand"
                  fill="#1A73E8"
                  radius={[0, 8, 8, 0]}
                  label={{ position: 'right', fill: '#6B7280' }}
                />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Weather Impact */}
        <Card>
          <CardHeader>
            <h3 className="text-gray-900">Weather Impact Correlation</h3>
            <p className="text-sm text-gray-500 mt-1">How weather affects ridership</p>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="p-4 bg-gradient-to-r from-yellow-50 to-orange-50 rounded-xl">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <Cloud className="w-5 h-5 text-orange-600" />
                    <span className="text-sm text-gray-900">Sunny Weather</span>
                  </div>
                  <span className="text-sm text-orange-700">-8% ridership</span>
                </div>
                <div className="w-full bg-white rounded-full h-2">
                  <div className="bg-orange-500 h-2 rounded-full" style={{ width: '45%' }} />
                </div>
              </div>

              <div className="p-4 bg-gradient-to-r from-blue-50 to-blue-100 rounded-xl">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <Cloud className="w-5 h-5 text-blue-600" />
                    <span className="text-sm text-gray-900">Rainy Weather</span>
                  </div>
                  <span className="text-sm text-blue-700">+23% ridership</span>
                </div>
                <div className="w-full bg-white rounded-full h-2">
                  <div className="bg-blue-500 h-2 rounded-full" style={{ width: '78%' }} />
                </div>
              </div>

              <div className="p-4 bg-gradient-to-r from-gray-50 to-gray-100 rounded-xl">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <Cloud className="w-5 h-5 text-gray-600" />
                    <span className="text-sm text-gray-900">Snowy Weather</span>
                  </div>
                  <span className="text-sm text-gray-700">+35% ridership</span>
                </div>
                <div className="w-full bg-white rounded-full h-2">
                  <div className="bg-gray-500 h-2 rounded-full" style={{ width: '92%' }} />
                </div>
              </div>

              <div className="pt-4 border-t border-gray-200">
                <div className="text-xs text-gray-600">
                  <span className="text-gray-900">Insight:</span> Ridership increases significantly during
                  adverse weather conditions. Consider increasing frequency on rainy/snowy days.
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Stop-level Forecast */}
      <Card>
        <CardHeader>
          <h3 className="text-gray-900">Stop-Level Crowd Forecasting</h3>
          <p className="text-sm text-gray-500 mt-1">Predicted crowd levels at major stops</p>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
            {stopForecast.map((stop) => (
              <div
                key={stop.stop}
                className="p-4 bg-gradient-to-br from-gray-50 to-white rounded-xl border border-gray-200 hover:shadow-lg transition-all"
              >
                <div className="flex items-center gap-2 mb-3">
                  <MapPin className="w-4 h-4 text-[#1A73E8]" />
                  <span className="text-sm text-gray-900">{stop.stop}</span>
                </div>
                <div className="mb-3">
                  <CrowdLevelBadge
                    level={stop.crowd as 'low' | 'medium' | 'high' | 'critical'}
                    size="sm"
                  />
                </div>
                <div className="space-y-2 text-xs">
                  <div className="flex justify-between">
                    <span className="text-gray-500">Wait Time</span>
                    <span className="text-gray-900">{stop.waitTime} min</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Passengers</span>
                    <span className="text-gray-900">{stop.passengers}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
