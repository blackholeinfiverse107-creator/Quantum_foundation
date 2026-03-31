import React, { useState } from 'react';
import { Navigation } from './components/Navigation';
import { OperatorSidebar } from './components/operator/OperatorSidebar';
import { MissionControl } from './components/operator/MissionControl';
import { RLRecommendations } from './components/operator/RLRecommendations';
import { DemandForecasting } from './components/operator/DemandForecasting';
import { EmotionSafety } from './components/operator/EmotionSafety';
import { DriverBehavior } from './components/operator/DriverBehavior';
import { PredictiveMaintenance } from './components/operator/PredictiveMaintenance';
import { FraudDetection } from './components/operator/FraudDetection';
import { Sustainability } from './components/operator/Sustainability';
import { PassengerHome } from './components/passenger/PassengerHome';
import { BusTracking } from './components/passenger/BusTracking';
import { DriverDashboard } from './components/driver/DriverDashboard';

type View = 'operator' | 'passenger' | 'driver';
type OperatorPage =
  | 'overview'
  | 'rl-recommendations'
  | 'demand-forecast'
  | 'emotion-safety'
  | 'driver-behavior'
  | 'maintenance'
  | 'fraud'
  | 'sustainability';

export default function App() {
  const [currentView, setCurrentView] = useState<View>('operator');
  const [operatorPage, setOperatorPage] = useState<OperatorPage>('overview');
  const [passengerScreen, setPassengerScreen] = useState<'home' | 'tracking'>('home');

  const renderOperatorContent = () => {
    switch (operatorPage) {
      case 'overview':
        return <MissionControl />;
      case 'rl-recommendations':
        return <RLRecommendations />;
      case 'demand-forecast':
        return <DemandForecasting />;
      case 'emotion-safety':
        return <EmotionSafety />;
      case 'driver-behavior':
        return <DriverBehavior />;
      case 'maintenance':
        return <PredictiveMaintenance />;
      case 'fraud':
        return <FraudDetection />;
      case 'sustainability':
        return <Sustainability />;
      default:
        return <MissionControl />;
    }
  };

  const renderContent = () => {
    switch (currentView) {
      case 'operator':
        return (
          <div className="flex">
            <OperatorSidebar activePage={operatorPage} onPageChange={(page) => setOperatorPage(page as OperatorPage)} />
            <div className="flex-1 p-8 overflow-y-auto">{renderOperatorContent()}</div>
          </div>
        );
      case 'passenger':
        return (
          <div>
            {passengerScreen === 'home' ? (
              <div onClick={() => setPassengerScreen('tracking')}>
                <PassengerHome />
              </div>
            ) : (
              <div>
                <BusTracking />
                <div className="fixed bottom-4 right-4">
                  <button
                    onClick={() => setPassengerScreen('home')}
                    className="px-6 py-3 bg-gradient-to-r from-[#1A73E8] to-[#34C759] text-white rounded-2xl shadow-2xl hover:shadow-3xl transition-all"
                  >
                    ← Back to Home
                  </button>
                </div>
              </div>
            )}
          </div>
        );
      case 'driver':
        return <DriverDashboard />;
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-[#F5F7FA]">
      <Navigation
        currentView={currentView}
        onViewChange={(view) => {
          setCurrentView(view);
          if (view === 'passenger') {
            setPassengerScreen('home');
          }
        }}
      />
      {renderContent()}
    </div>
  );
}
