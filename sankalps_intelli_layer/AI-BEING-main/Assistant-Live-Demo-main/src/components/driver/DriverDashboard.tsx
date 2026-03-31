import React from 'react';
import { Navigation, Users, Clock, AlertTriangle, Battery, Thermometer, MapPin } from 'lucide-react';
import { Card, CardContent } from '../Card';
import { CrowdLevelBadge } from '../CrowdLevelBadge';
import { GlowingIndicator } from '../GlowingIndicator';

export function DriverDashboard() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-green-50">
      {/* Header */}
      <div className="bg-gradient-to-r from-[#1A73E8] to-[#34C759] text-white">
        <div className="max-w-md mx-auto px-4 py-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="mb-1">Good Morning, Driver</h2>
              <p className="text-sm opacity-90">Bus B102 • Route 15</p>
            </div>
            <div className="w-14 h-14 bg-white bg-opacity-20 rounded-2xl flex items-center justify-center backdrop-blur">
              <span className="text-2xl">👤</span>
            </div>
          </div>

          {/* Current Status */}
          <div className="bg-white bg-opacity-20 rounded-2xl p-4 backdrop-blur">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <GlowingIndicator status="online" />
                <span className="text-sm">On Duty</span>
              </div>
              <span className="text-sm">Shift: 06:00 - 14:00</span>
            </div>
            <div className="grid grid-cols-3 gap-3 text-center">
              <div>
                <div className="text-2xl mb-1">4h 23m</div>
                <div className="text-xs opacity-80">Time Active</div>
              </div>
              <div>
                <div className="text-2xl mb-1">12</div>
                <div className="text-xs opacity-80">Trips Today</div>
              </div>
              <div>
                <div className="text-2xl mb-1">456</div>
                <div className="text-xs opacity-80">Passengers</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-md mx-auto px-4 py-6 space-y-4">
        {/* Next Route */}
        <Card>
          <CardContent className="p-5">
            <div className="flex items-center gap-2 text-[#1A73E8] mb-3">
              <Navigation className="w-5 h-5" />
              <span className="text-sm">Next Route</span>
            </div>
            <div className="flex items-start justify-between mb-4">
              <div>
                <h3 className="text-gray-900 mb-1">Downtown → Tech Park</h3>
                <div className="text-sm text-gray-500">Departure in 8 minutes</div>
              </div>
              <div className="text-right">
                <div className="text-2xl text-gray-900">18</div>
                <div className="text-xs text-gray-500">min trip</div>
              </div>
            </div>
            <div className="flex gap-2">
              <button className="flex-1 py-3 bg-gradient-to-r from-[#1A73E8] to-[#34C759] text-white rounded-xl hover:shadow-lg transition-all">
                Start Navigation
              </button>
              <button className="px-4 py-3 bg-gray-100 text-gray-700 rounded-xl hover:bg-gray-200 transition-colors">
                <MapPin className="w-5 h-5" />
              </button>
            </div>
          </CardContent>
        </Card>

        {/* Passenger Load */}
        <Card>
          <CardContent className="p-5">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <Users className="w-5 h-5 text-[#1A73E8]" />
                <span className="text-sm text-gray-900">Current Passenger Load</span>
              </div>
              <CrowdLevelBadge level="medium" size="sm" />
            </div>

            <div className="mb-3">
              <div className="flex items-center justify-between text-sm mb-2">
                <span className="text-gray-600">Occupancy</span>
                <span className="text-gray-900">38 / 60 seats</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div
                  className="bg-gradient-to-r from-[#1A73E8] to-[#34C759] h-3 rounded-full transition-all"
                  style={{ width: '63%' }}
                />
              </div>
            </div>

            <div className="p-3 bg-amber-50 border border-amber-200 rounded-xl flex items-start gap-2">
              <AlertTriangle className="w-4 h-4 text-amber-600 mt-0.5" />
              <div className="flex-1 text-xs text-amber-900">
                <span className="font-semibold">High crowd at next stop:</span> University Plaza expects 15+
                waiting passengers
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Bus Health Monitor */}
        <Card>
          <CardContent className="p-5">
            <div className="flex items-center gap-2 mb-4">
              <Thermometer className="w-5 h-5 text-[#1A73E8]" />
              <span className="text-sm text-gray-900">Bus Health Monitor</span>
            </div>

            <div className="grid grid-cols-2 gap-3 mb-4">
              <div className="p-3 bg-green-50 rounded-xl">
                <div className="flex items-center gap-2 mb-2">
                  <Thermometer className="w-4 h-4 text-green-600" />
                  <span className="text-xs text-green-700">Engine Temp</span>
                </div>
                <div className="text-xl text-green-900">82°C</div>
                <div className="text-xs text-green-600 mt-1">Normal</div>
              </div>

              <div className="p-3 bg-green-50 rounded-xl">
                <div className="flex items-center gap-2 mb-2">
                  <Battery className="w-4 h-4 text-green-600" />
                  <span className="text-xs text-green-700">Battery</span>
                </div>
                <div className="text-xl text-green-900">94%</div>
                <div className="text-xs text-green-600 mt-1">Excellent</div>
              </div>
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-between p-2 bg-gray-50 rounded-lg">
                <span className="text-xs text-gray-600">Brake Wear</span>
                <div className="flex items-center gap-2">
                  <div className="w-20 bg-gray-200 rounded-full h-1.5">
                    <div className="bg-green-500 h-1.5 rounded-full" style={{ width: '75%' }} />
                  </div>
                  <span className="text-xs text-gray-900">Good</span>
                </div>
              </div>

              <div className="flex items-center justify-between p-2 bg-gray-50 rounded-lg">
                <span className="text-xs text-gray-600">Tire Pressure</span>
                <div className="flex items-center gap-2">
                  <div className="w-20 bg-gray-200 rounded-full h-1.5">
                    <div className="bg-green-500 h-1.5 rounded-full" style={{ width: '88%' }} />
                  </div>
                  <span className="text-xs text-gray-900">Good</span>
                </div>
              </div>
            </div>

            <button className="w-full mt-3 py-2 bg-gray-100 text-gray-700 rounded-lg text-sm hover:bg-gray-200 transition-colors">
              View Full Diagnostics
            </button>
          </CardContent>
        </Card>

        {/* Safety Alerts */}
        <Card>
          <CardContent className="p-5">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <AlertTriangle className="w-5 h-5 text-[#1A73E8]" />
                <span className="text-sm text-gray-900">Safety Alerts</span>
              </div>
              <div className="bg-green-100 text-green-700 px-3 py-1 rounded-full text-xs">
                All Clear
              </div>
            </div>

            <div className="space-y-2">
              <div className="p-3 bg-green-50 border border-green-200 rounded-xl flex items-center gap-3">
                <div className="w-10 h-10 bg-green-200 rounded-lg flex items-center justify-center">
                  ✓
                </div>
                <div className="flex-1">
                  <div className="text-sm text-green-900">No Safety Issues</div>
                  <div className="text-xs text-green-700 mt-1">All systems operating normally</div>
                </div>
              </div>

              <div className="p-3 bg-blue-50 rounded-xl">
                <div className="text-xs text-blue-900 mb-2">Today's Safety Score</div>
                <div className="flex items-center gap-3">
                  <div className="flex-1">
                    <div className="w-full bg-blue-200 rounded-full h-2">
                      <div className="bg-blue-600 h-2 rounded-full" style={{ width: '95%' }} />
                    </div>
                  </div>
                  <div className="text-xl text-blue-900">95</div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <div className="grid grid-cols-2 gap-3">
          <button className="p-4 bg-white rounded-2xl shadow-sm border border-gray-100 hover:shadow-md transition-all">
            <Clock className="w-6 h-6 text-[#1A73E8] mb-2" />
            <div className="text-sm text-gray-900">Break Time</div>
          </button>

          <button className="p-4 bg-white rounded-2xl shadow-sm border border-gray-100 hover:shadow-md transition-all">
            <AlertTriangle className="w-6 h-6 text-[#FF5757] mb-2" />
            <div className="text-sm text-gray-900">Report Issue</div>
          </button>
        </div>
      </div>
    </div>
  );
}
