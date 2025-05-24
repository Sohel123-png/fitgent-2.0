import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  DevicePhoneMobileIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  ArrowPathIcon,
  WifiIcon,
  HeartIcon,
  FireIcon,
  MoonIcon
} from '@heroicons/react/24/outline';

interface ConnectionStatus {
  google_fit: boolean;
  apple_health: boolean;
  mi_band: boolean;
  last_sync?: string;
}

interface DeviceInfo {
  name: string;
  icon: string;
  status: 'connected' | 'disconnected' | 'syncing';
  description: string;
  features: string[];
}

const SmartwatchConnect: React.FC = () => {
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>({
    google_fit: false,
    apple_health: false,
    mi_band: false
  });
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState<string | null>(null);

  const devices: DeviceInfo[] = [
    {
      name: 'Google Fit',
      icon: '🏃‍♂️',
      status: connectionStatus.google_fit ? 'connected' : 'disconnected',
      description: 'Connect your Android smartwatch, Wear OS devices, and fitness apps',
      features: ['Steps tracking', 'Heart rate monitoring', 'Sleep analysis', 'Workout detection']
    },
    {
      name: 'Apple HealthKit',
      icon: '⌚',
      status: connectionStatus.apple_health ? 'connected' : 'disconnected',
      description: 'Sync data from Apple Watch and iPhone Health app',
      features: ['Comprehensive health metrics', 'ECG data', 'Blood oxygen', 'Activity rings']
    },
    {
      name: 'Mi Band / Noise',
      icon: '💪',
      status: connectionStatus.mi_band ? 'connected' : 'disconnected',
      description: 'Connect Mi Band, Noise, and other fitness trackers via Google Fit',
      features: ['24/7 heart rate', 'Sleep tracking', 'Stress monitoring', 'Long battery life']
    }
  ];

  // Check connection status
  const checkConnectionStatus = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      
      if (!token) {
        setLoading(false);
        return;
      }

      const response = await fetch('/api/google-fit/status', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setConnectionStatus(data);
      }
    } catch (error) {
      console.error('Error checking connection status:', error);
    } finally {
      setLoading(false);
    }
  };

  // Connect to Google Fit
  const connectGoogleFit = async () => {
    try {
      setSyncing('google_fit');
      window.location.href = '/api/google-fit/auth';
    } catch (error) {
      console.error('Error connecting to Google Fit:', error);
      setSyncing(null);
    }
  };

  // Connect to Apple Health (placeholder - would need native app)
  const connectAppleHealth = () => {
    alert('Apple HealthKit integration requires the FitGent mobile app. Download from the App Store!');
  };

  // Connect Mi Band via Google Fit
  const connectMiBand = () => {
    alert('To connect Mi Band or Noise devices:\n1. Install Mi Fit or Noise app\n2. Connect your device in the app\n3. Enable Google Fit sync in device settings\n4. Connect Google Fit above');
  };

  // Sync data
  const syncData = async (device: string) => {
    try {
      setSyncing(device);
      const token = localStorage.getItem('token');
      
      if (!token) {
        throw new Error('No authentication token');
      }

      const response = await fetch('/api/google-fit/health/sync-all', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        await checkConnectionStatus();
        // Show success message
        setTimeout(() => {
          alert('Data synced successfully!');
        }, 1000);
      }
    } catch (error) {
      console.error('Error syncing data:', error);
      alert('Error syncing data. Please try again.');
    } finally {
      setSyncing(null);
    }
  };

  useEffect(() => {
    checkConnectionStatus();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
          className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full"
        />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <DevicePhoneMobileIcon className="w-16 h-16 text-blue-500 mx-auto mb-4" />
          <h1 className="text-3xl font-bold text-gray-800 mb-2">Connect Your Smartwatch</h1>
          <p className="text-gray-600 max-w-2xl mx-auto">
            Sync your fitness data from smartwatches and fitness trackers to get personalized health insights and AI-powered recommendations.
          </p>
        </motion.div>

        {/* Connection Status Overview */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="bg-white rounded-2xl shadow-lg p-6 mb-8"
        >
          <h2 className="text-xl font-bold text-gray-800 mb-4">Connection Status</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="flex items-center space-x-3">
              <div className={`w-3 h-3 rounded-full ${connectionStatus.google_fit ? 'bg-green-500' : 'bg-gray-300'}`} />
              <span className="text-gray-700">Google Fit</span>
              {connectionStatus.google_fit && <CheckCircleIcon className="w-5 h-5 text-green-500" />}
            </div>
            <div className="flex items-center space-x-3">
              <div className={`w-3 h-3 rounded-full ${connectionStatus.apple_health ? 'bg-green-500' : 'bg-gray-300'}`} />
              <span className="text-gray-700">Apple Health</span>
              {connectionStatus.apple_health && <CheckCircleIcon className="w-5 h-5 text-green-500" />}
            </div>
            <div className="flex items-center space-x-3">
              <div className={`w-3 h-3 rounded-full ${connectionStatus.mi_band ? 'bg-green-500' : 'bg-gray-300'}`} />
              <span className="text-gray-700">Mi Band/Noise</span>
              {connectionStatus.mi_band && <CheckCircleIcon className="w-5 h-5 text-green-500" />}
            </div>
          </div>
          {connectionStatus.last_sync && (
            <p className="text-sm text-gray-500 mt-4">
              Last sync: {new Date(connectionStatus.last_sync).toLocaleString()}
            </p>
          )}
        </motion.div>

        {/* Device Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          {devices.map((device, index) => (
            <DeviceCard
              key={device.name}
              device={device}
              onConnect={() => {
                if (device.name === 'Google Fit') connectGoogleFit();
                else if (device.name === 'Apple HealthKit') connectAppleHealth();
                else connectMiBand();
              }}
              onSync={() => syncData(device.name.toLowerCase().replace(' ', '_'))}
              syncing={syncing === device.name.toLowerCase().replace(' ', '_')}
              index={index}
            />
          ))}
        </div>

        {/* Health Data Preview */}
        {(connectionStatus.google_fit || connectionStatus.apple_health) && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white rounded-2xl shadow-lg p-6"
          >
            <h2 className="text-xl font-bold text-gray-800 mb-4">Available Health Metrics</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <HealthMetricPreview
                icon={<FireIcon className="w-6 h-6 text-red-500" />}
                title="Steps & Activity"
                description="Daily steps, distance, active minutes"
              />
              <HealthMetricPreview
                icon={<HeartIcon className="w-6 h-6 text-pink-500" />}
                title="Heart Health"
                description="Heart rate, variability, zones"
              />
              <HealthMetricPreview
                icon={<MoonIcon className="w-6 h-6 text-purple-500" />}
                title="Sleep Analysis"
                description="Sleep duration, quality, stages"
              />
              <HealthMetricPreview
                icon={<WifiIcon className="w-6 h-6 text-blue-500" />}
                title="Stress & Recovery"
                description="Stress levels, recovery metrics"
              />
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
};

// Device Card Component
interface DeviceCardProps {
  device: DeviceInfo;
  onConnect: () => void;
  onSync: () => void;
  syncing: boolean;
  index: number;
}

const DeviceCard: React.FC<DeviceCardProps> = ({ device, onConnect, onSync, syncing, index }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1 }}
      className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow"
    >
      <div className="text-center mb-4">
        <div className="text-4xl mb-2">{device.icon}</div>
        <h3 className="text-lg font-bold text-gray-800">{device.name}</h3>
        <div className="flex items-center justify-center space-x-2 mt-2">
          <div className={`w-2 h-2 rounded-full ${
            device.status === 'connected' ? 'bg-green-500' : 
            device.status === 'syncing' ? 'bg-yellow-500' : 'bg-gray-300'
          }`} />
          <span className={`text-sm ${
            device.status === 'connected' ? 'text-green-600' : 
            device.status === 'syncing' ? 'text-yellow-600' : 'text-gray-500'
          }`}>
            {device.status === 'connected' ? 'Connected' : 
             device.status === 'syncing' ? 'Syncing...' : 'Not Connected'}
          </span>
        </div>
      </div>

      <p className="text-gray-600 text-sm mb-4">{device.description}</p>

      <div className="mb-4">
        <h4 className="text-sm font-medium text-gray-700 mb-2">Features:</h4>
        <ul className="text-xs text-gray-600 space-y-1">
          {device.features.map((feature, idx) => (
            <li key={idx} className="flex items-center space-x-2">
              <CheckCircleIcon className="w-3 h-3 text-green-500" />
              <span>{feature}</span>
            </li>
          ))}
        </ul>
      </div>

      <div className="space-y-2">
        {device.status === 'connected' ? (
          <button
            onClick={onSync}
            disabled={syncing}
            className="w-full bg-blue-500 text-white py-2 px-4 rounded-lg hover:bg-blue-600 transition-colors disabled:bg-gray-300 flex items-center justify-center space-x-2"
          >
            {syncing ? (
              <>
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                  className="w-4 h-4 border-2 border-white border-t-transparent rounded-full"
                />
                <span>Syncing...</span>
              </>
            ) : (
              <>
                <ArrowPathIcon className="w-4 h-4" />
                <span>Sync Data</span>
              </>
            )}
          </button>
        ) : (
          <button
            onClick={onConnect}
            className="w-full bg-green-500 text-white py-2 px-4 rounded-lg hover:bg-green-600 transition-colors flex items-center justify-center space-x-2"
          >
            <WifiIcon className="w-4 h-4" />
            <span>Connect</span>
          </button>
        )}
      </div>
    </motion.div>
  );
};

// Health Metric Preview Component
interface HealthMetricPreviewProps {
  icon: React.ReactNode;
  title: string;
  description: string;
}

const HealthMetricPreview: React.FC<HealthMetricPreviewProps> = ({ icon, title, description }) => {
  return (
    <div className="text-center p-4 border border-gray-200 rounded-lg">
      <div className="flex justify-center mb-2">{icon}</div>
      <h4 className="font-medium text-gray-800 text-sm mb-1">{title}</h4>
      <p className="text-xs text-gray-600">{description}</p>
    </div>
  );
};

export default SmartwatchConnect;
