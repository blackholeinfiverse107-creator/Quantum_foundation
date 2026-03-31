import React from 'react';
import { Leaf, TrendingDown, Zap, DollarSign } from 'lucide-react';
import { Card, CardHeader, CardContent } from '../Card';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

const emissionData = [
  { month: 'Jan', emissions: 1850, target: 1900 },
  { month: 'Feb', emissions: 1720, target: 1850 },
  { month: 'Mar', emissions: 1680, target: 1800 },
  { month: 'Apr', emissions: 1520, target: 1750 },
  { month: 'May', emissions: 1380, target: 1700 },
  { month: 'Jun', emissions: 1245, target: 1650 },
];

const routeEmissions = [
  { route: 'Route 15', emissions: 385, fuel: 142 },
  { route: 'Route 42', emissions: 342, fuel: 126 },
  { route: 'Route 8', emissions: 298, fuel: 110 },
  { route: 'Route 23', emissions: 265, fuel: 98 },
  { route: 'Route 7', emissions: 234, fuel: 86 },
];

export function Sustainability() {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-gray-900">Sustainability & CO₂ Analytics</h2>
        <p className="text-sm text-gray-500 mt-1">Environmental impact monitoring and optimization</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="border-l-4 border-emerald-500">
          <CardContent className="p-5">
            <div className="flex items-center justify-between mb-2">
              <Leaf className="w-8 h-8 text-emerald-600" />
              <div className="text-right">
                <div className="text-2xl text-emerald-900">1,245</div>
                <div className="text-xs text-emerald-600">kg</div>
              </div>
            </div>
            <div className="text-sm text-gray-600">Today's Emissions</div>
            <div className="flex items-center gap-1 text-xs text-green-700 mt-2">
              <TrendingDown className="w-3 h-3" />
              <span>-15% vs yesterday</span>
            </div>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-blue-500">
          <CardContent className="p-5">
            <div className="flex items-center justify-between mb-2">
              <Zap className="w-8 h-8 text-blue-600" />
              <div className="text-right">
                <div className="text-2xl text-blue-900">89%</div>
                <div className="text-xs text-blue-600">efficiency</div>
              </div>
            </div>
            <div className="text-sm text-gray-600">Fleet Efficiency</div>
            <div className="flex items-center gap-1 text-xs text-green-700 mt-2">
              <TrendingDown className="w-3 h-3" />
              <span>+3% this week</span>
            </div>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-green-500">
          <CardContent className="p-5">
            <div className="flex items-center justify-between mb-2">
              <Leaf className="w-8 h-8 text-green-600" />
              <div className="text-right">
                <div className="text-2xl text-green-900">340</div>
                <div className="text-xs text-green-600">kg/day</div>
              </div>
            </div>
            <div className="text-sm text-gray-600">CO₂ Saved</div>
            <div className="text-xs text-gray-500 mt-2">vs last month</div>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-purple-500">
          <CardContent className="p-5">
            <div className="flex items-center justify-between mb-2">
              <DollarSign className="w-8 h-8 text-purple-600" />
              <div className="text-right">
                <div className="text-2xl text-purple-900">$3.2K</div>
                <div className="text-xs text-purple-600">saved</div>
              </div>
            </div>
            <div className="text-sm text-gray-600">Fuel Cost Savings</div>
            <div className="text-xs text-gray-500 mt-2">this month</div>
          </CardContent>
        </Card>
      </div>

      {/* Emission Trend */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-gray-900">CO₂ Emission Trend</h3>
              <p className="text-sm text-gray-500 mt-1">Monthly emissions vs target</p>
            </div>
            <div className="flex items-center gap-2 text-sm text-green-700 bg-green-50 px-4 py-2 rounded-xl">
              <TrendingDown className="w-4 h-4" />
              <span>On track to meet 2025 goals</span>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={emissionData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
              <XAxis dataKey="month" stroke="#6B7280" />
              <YAxis stroke="#6B7280" label={{ value: 'CO₂ (kg)', angle: -90, position: 'insideLeft' }} />
              <Tooltip />
              <Legend />
              <Line
                type="monotone"
                dataKey="emissions"
                stroke="#34C759"
                strokeWidth={3}
                dot={{ r: 5, fill: '#34C759' }}
                name="Actual Emissions"
              />
              <Line
                type="monotone"
                dataKey="target"
                stroke="#FFB300"
                strokeWidth={2}
                strokeDasharray="5 5"
                dot={{ r: 4, fill: '#FFB300' }}
                name="Target"
              />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Route Emissions */}
        <Card>
          <CardHeader>
            <h3 className="text-gray-900">Route-Based Emissions</h3>
            <p className="text-sm text-gray-500 mt-1">CO₂ output by route</p>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={routeEmissions}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                <XAxis dataKey="route" stroke="#6B7280" />
                <YAxis stroke="#6B7280" />
                <Tooltip />
                <Bar dataKey="emissions" fill="#34C759" radius={[8, 8, 0, 0]} name="CO₂ (kg)" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Fuel Usage */}
        <Card>
          <CardHeader>
            <h3 className="text-gray-900">Fuel Consumption by Route</h3>
            <p className="text-sm text-gray-500 mt-1">Liters consumed</p>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={routeEmissions}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                <XAxis dataKey="route" stroke="#6B7280" />
                <YAxis stroke="#6B7280" />
                <Tooltip />
                <Bar dataKey="fuel" fill="#1A73E8" radius={[8, 8, 0, 0]} name="Fuel (L)" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Eco-Friendly Routing Suggestions */}
      <Card>
        <CardHeader>
          <h3 className="text-gray-900">Eco-Friendly Routing Suggestions</h3>
          <p className="text-sm text-gray-500 mt-1">AI-recommended optimizations for reduced emissions</p>
        </CardHeader>
        <CardContent className="space-y-3">
          {[
            {
              route: 'Route 15',
              suggestion: 'Optimize stop-and-go pattern at Main Street intersections',
              impact: -45,
              cost: 120,
            },
            {
              route: 'Route 42',
              suggestion: 'Use alternate route via Park Avenue during peak hours',
              impact: -38,
              cost: 95,
            },
            {
              route: 'Route 8',
              suggestion: 'Reduce idling time at University Plaza stop',
              impact: -28,
              cost: 75,
            },
          ].map((item, idx) => (
            <div
              key={idx}
              className="p-4 bg-gradient-to-r from-emerald-50 to-green-50 rounded-xl border border-emerald-200 hover:shadow-md transition-all"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <Leaf className="w-4 h-4 text-emerald-600" />
                    <span className="text-sm text-emerald-900">{item.route}</span>
                  </div>
                  <div className="text-sm text-gray-900 mb-2">{item.suggestion}</div>
                  <div className="flex gap-4 text-xs">
                    <div className="flex items-center gap-1">
                      <TrendingDown className="w-3 h-3 text-green-600" />
                      <span className="text-green-700">{item.impact} kg CO₂/day</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <DollarSign className="w-3 h-3 text-blue-600" />
                      <span className="text-blue-700">${item.cost} saved/month</span>
                    </div>
                  </div>
                </div>
                <button className="px-4 py-2 bg-emerald-600 text-white rounded-lg text-sm hover:bg-emerald-700 transition-colors whitespace-nowrap ml-4">
                  Implement
                </button>
              </div>
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Impact Summary */}
      <Card>
        <CardHeader>
          <h3 className="text-gray-900">Environmental Impact Summary</h3>
          <p className="text-sm text-gray-500 mt-1">This month's achievements</p>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-5 bg-gradient-to-br from-emerald-50 to-green-50 rounded-2xl">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-12 h-12 bg-emerald-600 rounded-xl flex items-center justify-center">
                  <Leaf className="w-6 h-6 text-white" />
                </div>
                <div>
                  <div className="text-2xl text-emerald-900">12.4</div>
                  <div className="text-xs text-emerald-600">tons CO₂</div>
                </div>
              </div>
              <div className="text-sm text-gray-700">Total emissions reduced</div>
              <div className="text-xs text-gray-500 mt-1">Equivalent to 156 trees planted</div>
            </div>

            <div className="p-5 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-2xl">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-12 h-12 bg-blue-600 rounded-xl flex items-center justify-center">
                  <Zap className="w-6 h-6 text-white" />
                </div>
                <div>
                  <div className="text-2xl text-blue-900">4,580</div>
                  <div className="text-xs text-blue-600">liters</div>
                </div>
              </div>
              <div className="text-sm text-gray-700">Fuel saved</div>
              <div className="text-xs text-gray-500 mt-1">vs traditional routing</div>
            </div>

            <div className="p-5 bg-gradient-to-br from-purple-50 to-pink-50 rounded-2xl">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-12 h-12 bg-purple-600 rounded-xl flex items-center justify-center">
                  <DollarSign className="w-6 h-6 text-white" />
                </div>
                <div>
                  <div className="text-2xl text-purple-900">$8.9K</div>
                  <div className="text-xs text-purple-600">saved</div>
                </div>
              </div>
              <div className="text-sm text-gray-700">Cost savings</div>
              <div className="text-xs text-gray-500 mt-1">from optimization</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
