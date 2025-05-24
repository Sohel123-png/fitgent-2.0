// User types
export interface User {
  id: string;
  name: string;
  email: string;
  avatar?: string;
  role: 'user' | 'admin';
  stats: UserStats;
}

export interface UserStats {
  calories: {
    current: number;
    goal: number;
  };
  water: {
    current: number;
    goal: number;
  };
  mood: 'great' | 'good' | 'okay' | 'bad';
  steps: number;
  sleep: number;
  weight: number;
}

// Meal types
export interface Meal {
  id: string;
  title: string;
  image: string;
  calories: number;
  category: string;
  tags: string[];
  nutritionalInfo: {
    protein: number;
    carbs: number;
    fat: number;
    fiber: number;
  };
  cookingSteps: string[];
}

// Chat types
export interface ChatMessage {
  id: string;
  sender: 'user' | 'assistant';
  message: string;
  timestamp: Date;
}

// Leaderboard types
export interface LeaderboardEntry {
  id: string;
  name: string;
  avatar: string;
  points: number;
}

// Task types
export interface Task {
  id: string;
  title: string;
  completed: boolean;
  dueDate?: Date;
  category: 'workout' | 'diet' | 'health' | 'other';
}

// Notification types
export interface Notification {
  id: string;
  title: string;
  message: string;
  type: 'achievement' | 'reminder' | 'alert';
  read: boolean;
  timestamp: Date;
}
