import React from 'react';
import { Bus, MapPin, AlertTriangle } from 'lucide-react';
import { Card, CardHeader, CardContent } from '../Card';
import { CrowdLevelBadge } from '../CrowdLevelBadge';

interface BusMarker {
  id: string;
  route: string;
  lat: number;
  lng: number;
  crowdLevel: 'low' | 'medium' | 'high' | 'critical';
  occupancy: number;
  hasAlert?: boolean;
}

const mockBuses: BusMarker[] = [
  { id: 'B101', route: 'Route 42', lat: 40.7589, lng: -73.9851, crowdLevel: 'low', occupancy: 35 },
  { id: 'B102', route: 'Route 15', lat: 40.7614, lng: -73.9776, crowdLevel: 'high', occupancy: 85, hasAlert: true },
  { id: 'B103', route: 'Route 8', lat: 40.7489, lng: -73.9680, crowdLevel: 'medium', occupancy: 62 },
  { id: 'B104', route: 'Route 42', lat: 40.7556, lng: -73.9870, crowdLevel: 'critical', occupancy: 98, hasAlert: true },
  { id: 'B105', route: 'Route 23', lat: 40.7520, lng: -73.9750, crowdLevel: 'low', occupancy: 28 },
  { id: 'B106', route: 'Route 15', lat: 40.7640, lng: -73.9820, crowdLevel: 'medium', occupancy: 55 },
];

interface FleetMapProps {
  onBusClick?: (busId: string) => void;
}

export function FleetMap({ onBusClick }: FleetMapProps) {
  return (
    <Card className="h-full">
      <CardHeader className="flex flex-row items-center justify-between">
        <div>
          <h3 className="text-gray-900">Real-Time Fleet Map</h3>
          <p className="text-sm text-gray-500 mt-1">Live bus locations with crowd & stress overlay</p>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <CrowdLevelBadge level="low" size="sm" />
            <CrowdLevelBadge level="medium" size="sm" />
            <CrowdLevelBadge level="high" size="sm" />
            <CrowdLevelBadge level="critical" size="sm" />
          </div>
        </div>
      </CardHeader>
      <CardContent className="p-0">
        <div className="relative bg-gradient-to-br from-blue-50 to-green-50 h-[500px] overflow-hidden">
          {/* Map Grid Background */}
          <div className="absolute inset-0 opacity-20">
            <svg width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
              <defs>
                <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
                  <path d="M 40 0 L 0 0 0 40" fill="none" stroke="gray" strokeWidth="0.5" />
                </pattern>
              </defs>
              <rect width="100%" height="100%" fill="url(#grid)" />
            </svg>
          </div>

          {/* Streets Simulation */}
          <svg className="absolute inset-0 w-full h-full" style={{ zIndex: 1 }}>
            <line x1="20%" y1="0" x2="20%" y2="100%" stroke="#D1D5DB" strokeWidth="3" />
            <line x1="50%" y1="0" x2="50%" y2="100%" stroke="#D1D5DB" strokeWidth="4" />
            <line x1="75%" y1="0" x2="75%" y2="100%" stroke="#D1D5DB" strokeWidth="3" />
            <line x1="0" y1="30%" x2="100%" y2="30%" stroke="#D1D5DB" strokeWidth="3" />
            <line x1="0" y1="60%" x2="100%" y2="60%" stroke="#D1D5DB" strokeWidth="4" />
            <line x1="0" y1="85%" x2="100%" y2="85%" stroke="#D1D5DB" strokeWidth="3" />
          </svg>

          {/* Bus Markers */}
          <div className="absolute inset-0" style={{ zIndex: 2 }}>
            {mockBuses.map((bus, idx) => {
              const posX = ((bus.lng + 73.9851) / 0.02) * 100;
              const posY = ((40.7650 - bus.lat) / 0.02) * 100;

              return (
                <div
                  key={bus.id}
                  className="absolute transform -translate-x-1/2 -translate-y-1/2 cursor-pointer group"
                  style={{ left: `${posX}%`, top: `${posY}%` }}
                  onClick={() => onBusClick?.(bus.id)}
                >
                  {/* Bus Icon */}
                  <div
                    className={`relative w-12 h-12 rounded-xl shadow-lg flex items-center justify-center transition-all hover:scale-110 ${
                      bus.crowdLevel === 'low'
                        ? 'bg-[#34C759]'
                        : bus.crowdLevel === 'medium'
                        ? 'bg-[#FFB300]'
                        : bus.crowdLevel === 'high'
                        ? 'bg-[#FF9500]'
                        : 'bg-[#FF5757]'
                    }`}
                  >
                    <Bus className="w-6 h-6 text-white" />
                    {bus.hasAlert && (
                      <div className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 rounded-full flex items-center justify-center pulse-glow">
                        <AlertTriangle className="w-3 h-3 text-white" />
                      </div>
                    )}
                  </div>

                  {/* Tooltip */}
                  <div className="absolute top-full mt-2 left-1/2 transform -translate-x-1/2 bg-white rounded-lg shadow-xl p-3 min-w-[200px] opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10">
                    <div className="text-sm">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-gray-900">{bus.id}</span>
                        <CrowdLevelBadge level={bus.crowdLevel} size="sm" />
                      </div>
                      <div className="text-xs text-gray-600 space-y-1">
                        <div>{bus.route}</div>
                        <div>Occupancy: {bus.occupancy}%</div>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}

            {/* Stop Markers */}
            {[
              { name: 'Central Station', x: 45, y: 58 },
              { name: 'Park Avenue', x: 70, y: 35 },
              { name: 'Tech Hub', x: 25, y: 75 },
            ].map((stop) => (
              <div
                key={stop.name}
                className="absolute transform -translate-x-1/2 -translate-y-1/2"
                style={{ left: `${stop.x}%`, top: `${stop.y}%` }}
              >
                <div className="w-3 h-3 bg-[#1A73E8] rounded-full border-2 border-white shadow-md" />
              </div>
            ))}
          </div>
        </div>

        {/* Map Legend */}
        <div className="p-4 bg-gray-50 border-t border-gray-100 flex items-center justify-between">
          <div className="flex items-center gap-6 text-xs text-gray-600">
            <div className="flex items-center gap-2">
              <Bus className="w-4 h-4" />
              <span>{mockBuses.length} Active Buses</span>
            </div>
            <div className="flex items-center gap-2">
              <MapPin className="w-4 h-4" />
              <span>42 Bus Stops</span>
            </div>
            <div className="flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-[#FF5757]" />
              <span>2 Active Alerts</span>
            </div>
          </div>
          <button className="text-xs text-[#1A73E8] hover:underline">View Full Screen Map</button>
        </div>
      </CardContent>
    </Card>
  );
}
