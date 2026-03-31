import React, { useState } from 'react';
import { Search, MapPin, Clock, Users, Cloud, Zap, Leaf, TrendingUp } from 'lucide-react';
import { Card, CardContent } from '../Card';
import { CrowdLevelBadge } from '../CrowdLevelBadge';

interface NearbyBus {
  id: string;
  route: string;
  destination: string;
  eta: number;
  crowdLevel: 'low' | 'medium' | 'high' | 'critical';
  stops: number;
}

const nearbyBuses: NearbyBus[] = [
  { id: 'B102', route: '15', destination: 'Downtown', eta: 3, crowdLevel: 'high', stops: 2 },
  { id: 'B045', route: '42', destination: 'Tech Park', eta: 5, crowdLevel: 'medium', stops: 3 },
  { id: 'B089', route: '8', destination: 'University', eta: 7, crowdLevel: 'low', stops: 4 },
  { id: 'B134', route: '23', destination: 'Airport', eta: 12, crowdLevel: 'medium', stops: 5 },
];

export function PassengerHome() {
  const [searchQuery, setSearchQuery] = useState('');

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-green-50">
      {/* Header */}
      <div className="bg-white shadow-sm">
        <div className="max-w-md mx-auto px-4 py-4">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-gray-900">Good Morning, Alex</h2>
              <p className="text-sm text-gray-500">Where are you heading today?</p>
            </div>
            <div className="w-12 h-12 bg-gradient-to-br from-[#1A73E8] to-[#34C759] rounded-full flex items-center justify-center text-white">
              A
            </div>
          </div>

          {/* Search Bar */}
          <div className="relative">
            <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Where are you going?"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-12 pr-4 py-4 bg-gray-50 border-0 rounded-2xl text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-[#1A73E8]"
            />
          </div>
        </div>
      </div>

      <div className="max-w-md mx-auto px-4 py-6 space-y-6">
        {/* Weather & Traffic Snapshot */}
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-gradient-to-br from-blue-100 to-blue-50 rounded-2xl p-4">
            <div className="flex items-center gap-2 mb-2">
              <Cloud className="w-5 h-5 text-blue-600" />
              <span className="text-sm text-blue-900">Weather</span>
            </div>
            <div className="text-2xl text-blue-900 mb-1">72°F</div>
            <div className="text-xs text-blue-700">Sunny & Clear</div>
          </div>

          <div className="bg-gradient-to-br from-green-100 to-green-50 rounded-2xl p-4">
            <div className="flex items-center gap-2 mb-2">
              <TrendingUp className="w-5 h-5 text-green-600" />
              <span className="text-sm text-green-900">Traffic</span>
            </div>
            <div className="text-2xl text-green-900 mb-1">Light</div>
            <div className="text-xs text-green-700">Smooth Flow</div>
          </div>
        </div>

        {/* Quick Actions */}
        <Card>
          <CardContent className="p-4">
            <div className="text-sm text-gray-900 mb-3">Quick Actions</div>
            <div className="grid grid-cols-3 gap-3">
              <button className="flex flex-col items-center gap-2 p-3 bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl hover:shadow-md transition-all">
                <div className="w-10 h-10 bg-[#1A73E8] rounded-xl flex items-center justify-center">
                  <Zap className="w-5 h-5 text-white" />
                </div>
                <span className="text-xs text-gray-700">Fastest Route</span>
              </button>

              <button className="flex flex-col items-center gap-2 p-3 bg-gradient-to-br from-green-50 to-green-100 rounded-xl hover:shadow-md transition-all">
                <div className="w-10 h-10 bg-[#34C759] rounded-xl flex items-center justify-center">
                  <Users className="w-5 h-5 text-white" />
                </div>
                <span className="text-xs text-gray-700">Least Crowded</span>
              </button>

              <button className="flex flex-col items-center gap-2 p-3 bg-gradient-to-br from-emerald-50 to-emerald-100 rounded-xl hover:shadow-md transition-all">
                <div className="w-10 h-10 bg-emerald-600 rounded-xl flex items-center justify-center">
                  <Leaf className="w-5 h-5 text-white" />
                </div>
                <span className="text-xs text-gray-700">Eco Route</span>
              </button>
            </div>
          </CardContent>
        </Card>

        {/* Nearby Buses */}
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between mb-4">
              <div className="text-sm text-gray-900">Nearest Buses</div>
              <button className="text-xs text-[#1A73E8] hover:underline">View All</button>
            </div>

            <div className="space-y-3">
              {nearbyBuses.map((bus) => (
                <div
                  key={bus.id}
                  className="p-4 bg-gradient-to-r from-gray-50 to-white rounded-xl border border-gray-100 hover:shadow-lg transition-all cursor-pointer"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <div className="w-12 h-12 bg-gradient-to-br from-[#1A73E8] to-[#34C759] rounded-xl flex items-center justify-center">
                        <span className="text-white">{bus.route}</span>
                      </div>
                      <div>
                        <div className="text-sm text-gray-900 mb-1">{bus.destination}</div>
                        <div className="flex items-center gap-2">
                          <CrowdLevelBadge level={bus.crowdLevel} size="sm" />
                        </div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-2xl text-[#1A73E8] mb-1">{bus.eta}</div>
                      <div className="text-xs text-gray-500">minutes</div>
                    </div>
                  </div>

                  <div className="flex items-center justify-between text-xs text-gray-600 pt-3 border-t border-gray-100">
                    <div className="flex items-center gap-1">
                      <MapPin className="w-3 h-3" />
                      <span>{bus.stops} stops away</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      <span>~{bus.stops * 2} min trip</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Saved Locations */}
        <Card>
          <CardContent className="p-4">
            <div className="text-sm text-gray-900 mb-3">Saved Locations</div>
            <div className="space-y-2">
              <button className="w-full flex items-center gap-3 p-3 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors">
                <div className="w-10 h-10 bg-purple-100 rounded-xl flex items-center justify-center">
                  <MapPin className="w-5 h-5 text-purple-600" />
                </div>
                <div className="flex-1 text-left">
                  <div className="text-sm text-gray-900">Home</div>
                  <div className="text-xs text-gray-500">123 Oak Street</div>
                </div>
              </button>

              <button className="w-full flex items-center gap-3 p-3 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors">
                <div className="w-10 h-10 bg-blue-100 rounded-xl flex items-center justify-center">
                  <MapPin className="w-5 h-5 text-blue-600" />
                </div>
                <div className="flex-1 text-left">
                  <div className="text-sm text-gray-900">Work</div>
                  <div className="text-xs text-gray-500">Tech Park, Building A</div>
                </div>
              </button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
