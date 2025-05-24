import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  HeartIcon,
  FireIcon,
  MoonIcon,
  BeakerIcon,
  TrophyIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  ClockIcon
} from '@heroicons/react/24/outline';
import { healthApi } from '../services/healthApi';

interface HealthMetrics {
  steps: number;
  calories_burned: number;
  heart_rate_avg: number;
  sleep_hours: number;
  weight_kg: number;
  distance_km: number;
  active_minutes: number;
  bmi: number;
  stress_level?: number;
}

interface WellnessScore {
  score: number;
  max_score: number;
  percentage: number;
  grade: string;
  grade_message: string;
  breakdown: {
    steps: number;
    sleep: number;
    activity: number;
    consistency: number;
    heart_health: number;
  };
  improvement_areas: string[];
}

interface Recommendation {
  type: string;
  priority: string;
  message: string;
  action: string;
  estimated_benefit: string;
  timing: string;
  icon?: string;
  badge?: string;
  points?: number;
}

interface HealthData {
  metrics: HealthMetrics;
  wellness_score: WellnessScore;
  recommendations: {
    hydration: Recommendation[];
    movement: Recommendation[];
    nutrition: Recommendation[];
    sleep: Recommendation[];
    stress: Recommendation[];
    study_breaks: Recommendation[];
    achievements: Recommendation[];
  };
}

const HealthDashboard: React.FC = () => {
  const [healthData, setHealthData] = useState<HealthData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [syncStatus, setSyncStatus] = useState<'idle' | 'syncing' | 'success' | 'error'>('idle');

  // Fetch health data from backend
  const fetchHealthData = async () => {
    try {
      setLoading(true);

      // Use healthApi service for all API calls
      const [healthResult, recommendationsResult, wellnessResult] = await Promise.all([
        healthApi.getComprehensiveHealthData(),
        healthApi.getAIRecommendations(),
        healthApi.getWellnessScore()
      ]);

      // Combine all data
      const combinedData: HealthData = {
        metrics: healthResult.data?.metrics || {
          steps: 0,
          calories_burned: 0,
          heart_rate_avg: 0,
          sleep_hours: 0,
          weight_kg: 0,
          distance_km: 0,
          active_minutes: 0,
          bmi: 0
        },
        wellness_score: wellnessResult.data?.wellness_score || {
          score: 0,
          max_score: 100,
          percentage: 0,
          grade: 'No Data',
          grade_message: 'Connect your smartwatch to get started',
          breakdown: {
            steps: 0,
            sleep: 0,
            activity: 0,
            consistency: 0,
            heart_health: 0
          },
          improvement_areas: []
        },
        recommendations: recommendationsResult.data?.recommendations || {
          hydration: [],
          movement: [],
          nutrition: [],
          sleep: [],
          stress: [],
          study_breaks: [],
          achievements: [],
          wellness_score: 0
        }
      };

      setHealthData(combinedData);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load health data. Please check your connection.');
      console.error('Error fetching health data:', err);
    } finally {
      setLoading(false);
    }
  };

  // Sync all health sources
  const syncHealthData = async () => {
    try {
      setSyncStatus('syncing');

      // Use healthApi service for sync
      await healthApi.syncAllHealthSources();

      setSyncStatus('success');

      // Refresh data after sync
      setTimeout(() => {
        fetchHealthData();
        setSyncStatus('idle');
      }, 1000);

    } catch (err) {
      setSyncStatus('error');
      console.error('Error syncing health data:', err);
      setTimeout(() => setSyncStatus('idle'), 3000);
    }
  };

  useEffect(() => {
    fetchHealthData();

    // Auto-refresh every 5 minutes
    const interval = setInterval(fetchHealthData, 5 * 60 * 1000);
    return () => clearInterval(interval);
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

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="bg-white p-8 rounded-xl shadow-lg text-center">
          <ExclamationTriangleIcon className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-bold text-gray-800 mb-2">Error Loading Health Data</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={fetchHealthData}
            className="bg-blue-500 text-white px-6 py-2 rounded-lg hover:bg-blue-600 transition-colors"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  if (!healthData) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="bg-white p-8 rounded-xl shadow-lg text-center">
          <BeakerIcon className="w-16 h-16 text-blue-500 mx-auto mb-4" />
          <h2 className="text-xl font-bold text-gray-800 mb-2">Connect Your Smartwatch</h2>
          <p className="text-gray-600 mb-4">Connect your smartwatch to get personalized health insights!</p>
          <button
            onClick={() => window.location.href = '/api/google-fit/auth'}
            className="bg-blue-500 text-white px-6 py-2 rounded-lg hover:bg-blue-600 transition-colors"
          >
            Connect Google Fit
          </button>
        </div>
      </div>
    );
  }

  const { metrics, wellness_score, recommendations } = healthData;

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-800 mb-2">Health Dashboard</h1>
              <p className="text-gray-600">Your personalized wellness insights powered by AI</p>
            </div>
            <button
              onClick={syncHealthData}
              disabled={syncStatus === 'syncing'}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
                syncStatus === 'syncing'
                  ? 'bg-gray-300 cursor-not-allowed'
                  : syncStatus === 'success'
                  ? 'bg-green-500 text-white'
                  : syncStatus === 'error'
                  ? 'bg-red-500 text-white'
                  : 'bg-blue-500 text-white hover:bg-blue-600'
              }`}
            >
              {syncStatus === 'syncing' && (
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                  className="w-4 h-4 border-2 border-white border-t-transparent rounded-full"
                />
              )}
              {syncStatus === 'success' && <CheckCircleIcon className="w-4 h-4" />}
              {syncStatus === 'error' && <ExclamationTriangleIcon className="w-4 h-4" />}
              {syncStatus === 'idle' && <ClockIcon className="w-4 h-4" />}
              <span>
                {syncStatus === 'syncing' ? 'Syncing...' :
                 syncStatus === 'success' ? 'Synced!' :
                 syncStatus === 'error' ? 'Error' : 'Sync Now'}
              </span>
            </button>
          </div>
        </motion.div>

        {/* Wellness Score Card */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="bg-white rounded-2xl shadow-lg p-6 mb-8"
        >
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold text-gray-800">Wellness Score</h2>
            <div className="flex items-center space-x-2">
              <TrophyIcon className="w-6 h-6 text-yellow-500" />
              <span className="text-2xl font-bold text-gray-800">{wellness_score.score}</span>
              <span className="text-gray-500">/ {wellness_score.max_score}</span>
            </div>
          </div>

          <div className="mb-4">
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-medium text-gray-600">{wellness_score.grade}</span>
              <span className="text-sm text-gray-500">{wellness_score.percentage}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${wellness_score.percentage}%` }}
                transition={{ duration: 1, ease: "easeOut" }}
                className={`h-3 rounded-full ${
                  wellness_score.percentage >= 80 ? 'bg-green-500' :
                  wellness_score.percentage >= 60 ? 'bg-yellow-500' : 'bg-red-500'
                }`}
              />
            </div>
          </div>

          <p className="text-gray-600 mb-4">{wellness_score.grade_message}</p>

          {/* Score Breakdown */}
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            {Object.entries(wellness_score.breakdown).map(([key, value]) => (
              <div key={key} className="text-center">
                <div className="text-lg font-bold text-gray-800">{value}</div>
                <div className="text-xs text-gray-500 capitalize">{key.replace('_', ' ')}</div>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Health Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <HealthMetricCard
            title="Steps"
            value={metrics.steps.toLocaleString()}
            goal="10,000"
            icon={<FireIcon className="w-6 h-6" />}
            color="blue"
            progress={(metrics.steps / 10000) * 100}
          />
          <HealthMetricCard
            title="Calories Burned"
            value={metrics.calories_burned.toString()}
            goal="500"
            icon={<FireIcon className="w-6 h-6" />}
            color="red"
            progress={(metrics.calories_burned / 500) * 100}
          />
          <HealthMetricCard
            title="Heart Rate"
            value={`${metrics.heart_rate_avg} bpm`}
            goal="60-80"
            icon={<HeartIcon className="w-6 h-6" />}
            color="pink"
            progress={metrics.heart_rate_avg > 0 ? 100 : 0}
          />
          <HealthMetricCard
            title="Sleep"
            value={`${metrics.sleep_hours}h`}
            goal="8h"
            icon={<MoonIcon className="w-6 h-6" />}
            color="purple"
            progress={(metrics.sleep_hours / 8) * 100}
          />
        </div>

        {/* Recommendations Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Urgent Recommendations */}
          <RecommendationSection
            title="Priority Actions"
            recommendations={[
              ...recommendations.movement.filter(r => r.priority === 'high'),
              ...recommendations.hydration.filter(r => r.priority === 'high'),
              ...recommendations.stress.filter(r => r.priority === 'high')
            ]}
            color="red"
          />

          {/* Achievements */}
          <RecommendationSection
            title="Achievements"
            recommendations={recommendations.achievements}
            color="green"
          />
        </div>
      </div>
    </div>
  );
};

// Health Metric Card Component
interface HealthMetricCardProps {
  title: string;
  value: string;
  goal: string;
  icon: React.ReactNode;
  color: string;
  progress: number;
}

const HealthMetricCard: React.FC<HealthMetricCardProps> = ({
  title, value, goal, icon, color, progress
}) => {
  const colorClasses = {
    blue: 'text-blue-500 bg-blue-50',
    red: 'text-red-500 bg-red-50',
    pink: 'text-pink-500 bg-pink-50',
    purple: 'text-purple-500 bg-purple-50',
    green: 'text-green-500 bg-green-50'
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-xl shadow-lg p-6"
    >
      <div className="flex items-center justify-between mb-4">
        <div className={`p-3 rounded-lg ${colorClasses[color as keyof typeof colorClasses]}`}>
          {icon}
        </div>
        <div className="text-right">
          <div className="text-2xl font-bold text-gray-800">{value}</div>
          <div className="text-sm text-gray-500">Goal: {goal}</div>
        </div>
      </div>

      <div className="mb-2">
        <div className="flex justify-between items-center mb-1">
          <span className="text-sm font-medium text-gray-600">{title}</span>
          <span className="text-sm text-gray-500">{Math.min(100, Math.round(progress))}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${Math.min(100, progress)}%` }}
            transition={{ duration: 1, ease: "easeOut" }}
            className={`h-2 rounded-full ${
              progress >= 100 ? 'bg-green-500' :
              progress >= 70 ? 'bg-yellow-500' : 'bg-gray-400'
            }`}
          />
        </div>
      </div>
    </motion.div>
  );
};

// Recommendation Section Component
interface RecommendationSectionProps {
  title: string;
  recommendations: Recommendation[];
  color: string;
}

const RecommendationSection: React.FC<RecommendationSectionProps> = ({
  title, recommendations, color
}) => {
  if (recommendations.length === 0) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-xl shadow-lg p-6"
    >
      <h3 className="text-lg font-bold text-gray-800 mb-4">{title}</h3>
      <div className="space-y-4">
        {recommendations.slice(0, 3).map((rec, index) => (
          <div key={index} className="border-l-4 border-blue-500 pl-4">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <p className="font-medium text-gray-800">{rec.message}</p>
                <p className="text-sm text-gray-600 mt-1">{rec.action}</p>
                {rec.estimated_benefit && (
                  <p className="text-xs text-green-600 mt-1">💡 {rec.estimated_benefit}</p>
                )}
              </div>
              {rec.icon && <span className="text-2xl ml-2">{rec.icon}</span>}
            </div>
          </div>
        ))}
      </div>
    </motion.div>
  );
};

export default HealthDashboard;
