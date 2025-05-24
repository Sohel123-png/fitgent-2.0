/**
 * Health API Service for FitGent 2.0
 * Handles communication with the Flask backend for health data and smartwatch integration
 */

const API_BASE_URL = process.env.REACT_APP_API_URL ||
  (process.env.NODE_ENV === 'production'
    ? 'https://fitgent-backend.onrender.com'
    : 'http://localhost:5000');

interface ApiResponse<T> {
  success: boolean;
  data?: T;
  msg?: string;
  error?: string;
}

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

interface HealthRecommendations {
  hydration: Recommendation[];
  movement: Recommendation[];
  nutrition: Recommendation[];
  sleep: Recommendation[];
  stress: Recommendation[];
  study_breaks: Recommendation[];
  achievements: Recommendation[];
  wellness_score: number;
}

class HealthApiService {
  private getAuthHeaders(): HeadersInit {
    const token = localStorage.getItem('token');
    return {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` })
    };
  }

  private async makeRequest<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        headers: {
          ...this.getAuthHeaders(),
          ...options.headers
        }
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.msg || data.error || 'Request failed');
      }

      return data;
    } catch (error) {
      console.error(`API Error (${endpoint}):`, error);
      throw error;
    }
  }

  // Google Fit Authentication
  async initiateGoogleFitAuth(): Promise<string> {
    return `${API_BASE_URL}/api/google-fit/auth`;
  }

  // Get comprehensive health data
  async getComprehensiveHealthData(): Promise<ApiResponse<{
    metrics: HealthMetrics;
    sources: string[];
    timestamp: string;
  }>> {
    return this.makeRequest('/api/google-fit/health/comprehensive');
  }

  // Sync all health sources
  async syncAllHealthSources(): Promise<ApiResponse<{
    health_data: { metrics: HealthMetrics };
    recommendations: HealthRecommendations;
    sync_timestamp: string;
  }>> {
    return this.makeRequest('/api/google-fit/health/sync-all', {
      method: 'POST'
    });
  }

  // Get AI recommendations
  async getAIRecommendations(): Promise<ApiResponse<{
    recommendations: HealthRecommendations;
    health_data: { metrics: HealthMetrics };
    timestamp: string;
  }>> {
    return this.makeRequest('/api/health-ai/recommendations');
  }

  // Get wellness score
  async getWellnessScore(): Promise<ApiResponse<{
    wellness_score: WellnessScore;
    metrics: HealthMetrics;
    trends: any;
  }>> {
    return this.makeRequest('/api/health-ai/wellness-score');
  }

  // Get weekly health summary
  async getWeeklyHealthSummary(): Promise<ApiResponse<{
    weekly_summary: any;
    wellness_score: any;
    period: {
      start_date: string;
      end_date: string;
    };
  }>> {
    return this.makeRequest('/api/google-fit/health/weekly-summary');
  }

  // Check connection status
  async getConnectionStatus(): Promise<ApiResponse<{
    google_fit: boolean;
    apple_health: boolean;
    mi_band: boolean;
    last_sync?: string;
  }>> {
    return this.makeRequest('/api/google-fit/status');
  }

  // Get fitness data (existing endpoint)
  async getFitnessData(): Promise<ApiResponse<any>> {
    return this.makeRequest('/api/google-fit/data');
  }

  // Sync fitness data (existing endpoint)
  async syncFitnessData(): Promise<ApiResponse<any>> {
    return this.makeRequest('/api/google-fit/sync', {
      method: 'POST'
    });
  }
}

// Create and export a singleton instance
export const healthApi = new HealthApiService();

// Export types for use in components
export type {
  HealthMetrics,
  WellnessScore,
  Recommendation,
  HealthRecommendations,
  ApiResponse
};

// Utility functions for health data
export const healthUtils = {
  // Calculate BMI
  calculateBMI(weight_kg: number, height_cm: number): number {
    const height_m = height_cm / 100;
    return weight_kg / (height_m * height_m);
  },

  // Get BMI category
  getBMICategory(bmi: number): string {
    if (bmi < 18.5) return 'Underweight';
    if (bmi < 25) return 'Normal';
    if (bmi < 30) return 'Overweight';
    return 'Obese';
  },

  // Format step count
  formatSteps(steps: number): string {
    if (steps >= 1000) {
      return `${(steps / 1000).toFixed(1)}K`;
    }
    return steps.toString();
  },

  // Get heart rate zone
  getHeartRateZone(heartRate: number, age: number): string {
    const maxHR = 220 - age;
    const percentage = (heartRate / maxHR) * 100;

    if (percentage < 50) return 'Resting';
    if (percentage < 60) return 'Fat Burn';
    if (percentage < 70) return 'Aerobic';
    if (percentage < 85) return 'Anaerobic';
    return 'Max Effort';
  },

  // Get sleep quality
  getSleepQuality(hours: number): string {
    if (hours >= 7 && hours <= 9) return 'Excellent';
    if (hours >= 6 && hours < 7) return 'Good';
    if (hours >= 5 && hours < 6) return 'Fair';
    return 'Poor';
  },

  // Calculate calories needed based on activity
  calculateCalorieNeeds(weight_kg: number, activityLevel: 'low' | 'moderate' | 'high'): number {
    const baseCalories = weight_kg * 24; // BMR approximation
    const multipliers = {
      low: 1.2,
      moderate: 1.5,
      high: 1.8
    };
    return Math.round(baseCalories * multipliers[activityLevel]);
  },

  // Get hydration recommendation
  getHydrationRecommendation(weight_kg: number, activityLevel: number = 0): number {
    // Base: 35ml per kg + activity bonus
    return Math.round(weight_kg * 35 + activityLevel * 500);
  },

  // Format time duration
  formatDuration(minutes: number): string {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;

    if (hours > 0) {
      return `${hours}h ${mins}m`;
    }
    return `${mins}m`;
  },

  // Get wellness grade color
  getWellnessGradeColor(grade: string): string {
    switch (grade.toLowerCase()) {
      case 'excellent': return 'text-green-600';
      case 'good': return 'text-blue-600';
      case 'fair': return 'text-yellow-600';
      case 'needs improvement': return 'text-red-600';
      default: return 'text-gray-600';
    }
  },

  // Get recommendation priority color
  getRecommendationPriorityColor(priority: string): string {
    switch (priority.toLowerCase()) {
      case 'high': return 'border-red-500 bg-red-50';
      case 'medium': return 'border-yellow-500 bg-yellow-50';
      case 'low': return 'border-blue-500 bg-blue-50';
      default: return 'border-gray-500 bg-gray-50';
    }
  }
};
