import React, { useState } from 'react';
import Dashboard from './components/Dashboard';
import HealthDashboard from './components/HealthDashboard';
import SmartwatchConnect from './components/SmartwatchConnect';
import './App.css';

function App() {
  const [currentView, setCurrentView] = useState<'dashboard' | 'health' | 'connect'>('dashboard');

  const renderCurrentView = () => {
    switch (currentView) {
      case 'health':
        return <HealthDashboard />;
      case 'connect':
        return <SmartwatchConnect />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="App">
      {/* Navigation Bar */}
      <nav className="bg-white shadow-lg border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-8">
              <h1 className="text-xl font-bold text-gray-800">FitGent 2.0</h1>
              <div className="flex space-x-4">
                <button
                  onClick={() => setCurrentView('dashboard')}
                  className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    currentView === 'dashboard'
                      ? 'bg-blue-100 text-blue-700'
                      : 'text-gray-500 hover:text-gray-700'
                  }`}
                >
                  Dashboard
                </button>
                <button
                  onClick={() => setCurrentView('health')}
                  className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    currentView === 'health'
                      ? 'bg-blue-100 text-blue-700'
                      : 'text-gray-500 hover:text-gray-700'
                  }`}
                >
                  Health Insights
                </button>
                <button
                  onClick={() => setCurrentView('connect')}
                  className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    currentView === 'connect'
                      ? 'bg-blue-100 text-blue-700'
                      : 'text-gray-500 hover:text-gray-700'
                  }`}
                >
                  Connect Device
                </button>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                <span className="text-white text-sm font-medium">RS</span>
              </div>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      {renderCurrentView()}
    </div>
  );
}

export default App;
