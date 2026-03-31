import React, { useState } from 'react';
import { MapPin, Bus, Clock, Users, AlertCircle, Bell } from 'lucide-react';
import { Card, CardContent } from '../Card';
import { CrowdLevelBadge } from '../CrowdLevelBadge';

export function BusTracking() {
  const [reminderSet, setReminderSet] = useState(false);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-green-50">
      {/* Map View */}
      <div className="relative h-[400px] bg-gradient-to-br from-blue-100 to-green-100 overflow-hidden">
        {/* Map Grid */}
        <div className="absolute inset-0 opacity-20">
          <svg width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <pattern id="passenger-grid" width="40" height="40" patternUnits="userSpaceOnUse">
                <path d="M 40 0 L 0 0 0 40" fill="none" stroke="gray" strokeWidth="0.5" />
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#passenger-grid)" />
          </svg>
        </div>

        {/* Streets */}
        <svg className="absolute inset-0 w-full h-full" style={{ zIndex: 1 }}>
          <line x1="30%" y1="0" x2="30%" y2="100%" stroke="#D1D5DB" strokeWidth="4" />
          <line x1="70%" y1="0" x2="70%" y2="100%" stroke="#D1D5DB" strokeWidth="4" />
          <line x1="0" y1="40%" x2="100%" y2="40%" stroke="#D1D5DB" strokeWidth="4" />
          <line x1="0" y1="70%" x2="100%" y2="70%" stroke="#D1D5DB" strokeWidth="4" />
        </svg>

        {/* User Location */}
        <div className="absolute left-1/2 top-1/2 transform -translate-x-1/2 -translate-y-1/2" style={{ zIndex: 3 }}>
          <div className="relative">
            <div className="w-6 h-6 bg-[#1A73E8] rounded-full border-4 border-white shadow-lg pulse-glow" />
            <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
              <div className="w-12 h-12 bg-[#1A73E8] opacity-20 rounded-full animate-ping" />
            </div>
          </div>
          <div className="absolute top-full mt-2 left-1/2 transform -translate-x-1/2 bg-white rounded-lg shadow-xl px-3 py-1 whitespace-nowrap text-xs text-gray-900">
            You are here
          </div>
        </div>

        {/* Bus Location */}
        <div className="absolute left-[35%] top-[30%]" style={{ zIndex: 2 }}>
          <div className="w-14 h-14 bg-[#34C759] rounded-2xl shadow-xl flex items-center justify-center pulse-glow">
            <Bus className="w-7 h-7 text-white" />
          </div>
          <div className="absolute -top-2 -right-2 w-6 h-6 bg-[#1A73E8] text-white rounded-full flex items-center justify-center text-xs">
            15
          </div>
        </div>

        {/* Destination */}
        <div className="absolute left-[75%] top-[75%]" style={{ zIndex: 2 }}>
          <div className="w-10 h-10 bg-red-500 rounded-full border-4 border-white shadow-lg flex items-center justify-center">
            <MapPin className="w-5 h-5 text-white" />
          </div>
        </div>

        {/* Route Line */}
        <svg className="absolute inset-0 w-full h-full" style={{ zIndex: 1 }}>
          <path
            d="M 50% 50% Q 42% 40%, 35% 30%"
            stroke="#34C759"
            strokeWidth="3"
            fill="none"
            strokeDasharray="10 5"
          />
          <path
            d="M 50% 50% Q 62% 62%, 75% 75%"
            stroke="#1A73E8"
            strokeWidth="3"
            fill="none"
            strokeDasharray="10 5"
          />
        </svg>

        {/* Back Button */}
        <button className="absolute top-4 left-4 w-10 h-10 bg-white rounded-full shadow-lg flex items-center justify-center hover:shadow-xl transition-shadow" style={{ zIndex: 4 }}>
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
        </button>
      </div>

      {/* Bus Details Card */}
      <div className="max-w-md mx-auto px-4 -mt-10 relative z-10">
        <Card className="shadow-2xl">
          <CardContent className="p-6">
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="w-14 h-14 bg-gradient-to-br from-[#1A73E8] to-[#34C759] rounded-2xl flex items-center justify-center">
                  <span className="text-white text-xl">15</span>
                </div>
                <div>
                  <h3 className="text-gray-900 mb-1">Route 15 Express</h3>
                  <div className="text-sm text-gray-500">Bus ID: B102</div>
                </div>
              </div>
              <CrowdLevelBadge level="medium" />
            </div>

            {/* ETA */}
            <div className="mb-4 p-4 bg-gradient-to-r from-blue-50 to-blue-100 rounded-2xl">
              <div className="text-sm text-blue-700 mb-1">Arriving in</div>
              <div className="flex items-baseline gap-2">
                <span className="text-4xl text-blue-900">3</span>
                <span className="text-lg text-blue-700">minutes</span>
              </div>
              <div className="mt-2 text-xs text-blue-600">Next bus in 12 minutes</div>
            </div>

            {/* Details Grid */}
            <div className="grid grid-cols-3 gap-3 mb-4">
              <div className="text-center p-3 bg-gray-50 rounded-xl">
                <Users className="w-5 h-5 text-gray-600 mx-auto mb-1" />
                <div className="text-xs text-gray-500 mb-1">Occupancy</div>
                <div className="text-sm text-gray-900">62%</div>
              </div>

              <div className="text-center p-3 bg-gray-50 rounded-xl">
                <Clock className="w-5 h-5 text-gray-600 mx-auto mb-1" />
                <div className="text-xs text-gray-500 mb-1">Trip Time</div>
                <div className="text-sm text-gray-900">~18 min</div>
              </div>

              <div className="text-center p-3 bg-gray-50 rounded-xl">
                <MapPin className="w-5 h-5 text-gray-600 mx-auto mb-1" />
                <div className="text-xs text-gray-500 mb-1">Stops</div>
                <div className="text-sm text-gray-900">8 stops</div>
              </div>
            </div>

            {/* Stress Level */}
            <div className="mb-4 p-3 bg-green-50 rounded-xl">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 bg-green-200 rounded-lg flex items-center justify-center">
                    😊
                  </div>
                  <div>
                    <div className="text-xs text-green-700">Comfort Level</div>
                    <div className="text-sm text-green-900">Calm & Comfortable</div>
                  </div>
                </div>
                <div className="text-xs text-green-700">Low Stress</div>
              </div>
            </div>

            {/* Delay Warning */}
            <div className="mb-4 p-3 bg-amber-50 border border-amber-200 rounded-xl flex items-start gap-2">
              <AlertCircle className="w-4 h-4 text-amber-600 mt-0.5" />
              <div className="flex-1">
                <div className="text-xs text-amber-900">
                  <span className="font-semibold">Minor Delay Expected:</span> Light traffic on Main Street may cause
                  1-2 min delay
                </div>
              </div>
            </div>

            {/* Reminder Button */}
            <button
              onClick={() => setReminderSet(!reminderSet)}
              className={`w-full flex items-center justify-center gap-2 py-3 rounded-xl transition-all ${
                reminderSet
                  ? 'bg-[#34C759] text-white'
                  : 'bg-gradient-to-r from-[#1A73E8] to-[#34C759] text-white hover:shadow-lg'
              }`}
            >
              <Bell className="w-5 h-5" />
              <span>{reminderSet ? 'Reminder Set ✓' : 'Remind Me 5 Min Before'}</span>
            </button>
          </CardContent>
        </Card>

        {/* Upcoming Stops */}
        <Card className="mt-4 mb-6">
          <CardContent className="p-4">
            <div className="text-sm text-gray-900 mb-3">Upcoming Stops</div>
            <div className="space-y-3">
              {[
                { name: 'Main Street', time: '2 min', current: true },
                { name: 'Park Avenue', time: '5 min', current: false },
                { name: 'Tech Park (Your Stop)', time: '8 min', current: false },
                { name: 'University Plaza', time: '12 min', current: false },
              ].map((stop, idx) => (
                <div key={idx} className="flex items-center gap-3">
                  <div className="relative flex flex-col items-center">
                    <div
                      className={`w-3 h-3 rounded-full ${
                        stop.current ? 'bg-[#1A73E8] pulse-glow' : 'bg-gray-300'
                      }`}
                    />
                    {idx < 3 && <div className="w-0.5 h-8 bg-gray-200 mt-1" />}
                  </div>
                  <div className="flex-1">
                    <div className={`text-sm ${stop.current ? 'text-gray-900' : 'text-gray-600'}`}>
                      {stop.name}
                    </div>
                    <div className="text-xs text-gray-500">{stop.time}</div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
