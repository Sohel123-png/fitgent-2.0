import React, { useState, useEffect } from 'react';
import Navbar from './Navbar';
import DailyProgress from './DailyProgress';
import MealPlanner from './MealPlanner';
import ChatAssistant from './ChatAssistant';
import Leaderboard from './Leaderboard';
import TaskCompletion from './TaskCompletion';
import RealTimePlanner from './RealTimePlanner';
import AchievementNotification from './AchievementNotification';
import { ChatMessage, LeaderboardEntry, Meal, Notification, Task, User, UserStats } from '../types';
import { v4 as uuidv4 } from 'uuid';

// Mock data
const mockUser: User = {
  id: '1',
  name: 'Rahul Sharma',
  email: 'rahul.sharma@example.com',
  avatar: 'https://randomuser.me/api/portraits/men/32.jpg',
  role: 'user',
  stats: {
    calories: { current: 1300, goal: 2200 },
    water: { current: 8, goal: 12 },
    mood: 'okay',
    steps: 8500,
    sleep: 7.5,
    weight: 70
  }
};

const mockUserStats: UserStats = mockUser.stats;

const mockMeal: Meal = {
  id: '1',
  title: 'Oats + Banana Smoothie',
  image: 'https://images.unsplash.com/photo-1623428187969-5da2dcea5ebf?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1064&q=80',
  calories: 450,
  category: 'Energy Refill',
  tags: ['breakfast', 'energy', 'protein'],
  nutritionalInfo: {
    protein: 15,
    carbs: 65,
    fat: 10,
    fiber: 8
  },
  cookingSteps: [
    'Add 1 cup of rolled oats to a blender',
    'Add 1 ripe banana, sliced',
    'Add 1 cup of milk or plant-based alternative',
    'Add 1 tablespoon of honey or maple syrup',
    'Blend until smooth and creamy',
    'Pour into a glass and enjoy!'
  ]
};

const mockChatMessages: ChatMessage[] = [
  {
    id: '1',
    sender: 'user',
    message: 'Low mood hai, kya light meal suggest karoge?',
    timestamp: new Date()
  },
  {
    id: '2',
    sender: 'assistant',
    message: 'Kaise ho! Aaj soba oats+banana smoothie try karo, simple and nourishin, sahi mood fresh ho 👍 👍',
    timestamp: new Date()
  }
];

const mockLeaderboardEntries: LeaderboardEntry[] = [
  {
    id: '1',
    name: 'Priya',
    avatar: 'https://randomuser.me/api/portraits/women/44.jpg',
    points: 11250
  },
  {
    id: '2',
    name: 'Aditya',
    avatar: 'https://randomuser.me/api/portraits/men/32.jpg',
    points: 10650
  },
  {
    id: '3',
    name: 'Sunita',
    avatar: 'https://randomuser.me/api/portraits/women/68.jpg',
    points: 10600
  },
  {
    id: '4',
    name: 'Anil',
    avatar: 'https://randomuser.me/api/portraits/men/75.jpg',
    points: 10400
  }
];

const mockTasks: Task[] = [
  {
    id: '1',
    title: 'Morning Workout',
    completed: true,
    category: 'workout'
  },
  {
    id: '2',
    title: 'Drink 2L Water',
    completed: false,
    category: 'health'
  },
  {
    id: '3',
    title: 'Protein Lunch',
    completed: false,
    category: 'diet'
  },
  {
    id: '4',
    title: 'Evening Walk',
    completed: false,
    category: 'workout'
  },
  {
    id: '5',
    title: 'Meditation',
    completed: false,
    category: 'health'
  }
];

const mockNotifications: Notification[] = [
  {
    id: '1',
    title: 'Achievement Unlocked',
    message: 'You completed your first workout streak!',
    type: 'achievement',
    read: false,
    timestamp: new Date()
  },
  {
    id: '2',
    title: 'Meal Reminder',
    message: 'Time for your protein-rich lunch!',
    type: 'reminder',
    read: false,
    timestamp: new Date()
  },
  {
    id: '3',
    title: 'Water Alert',
    message: 'You are behind on your water intake goal',
    type: 'alert',
    read: true,
    timestamp: new Date()
  }
];

const Dashboard: React.FC = () => {
  // Navigation state
  const [activeNavItem, setActiveNavItem] = useState('dashboard');

  // User data state
  const [user, setUser] = useState<User>(mockUser);
  const [userStats, setUserStats] = useState<UserStats>(mockUserStats);

  // Chat state
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>(mockChatMessages);

  // Tasks state
  const [tasks, setTasks] = useState<Task[]>(mockTasks);

  // Notifications state
  const [notifications, setNotifications] = useState<Notification[]>(mockNotifications);
  const [showNotification, setShowNotification] = useState<boolean>(true);

  // Leaderboard state
  const [leaderboardEntries, setLeaderboardEntries] = useState<LeaderboardEntry[]>(mockLeaderboardEntries);

  // Meal state
  const [currentMeal, setCurrentMeal] = useState<Meal>(mockMeal);

  // Handle sending a new chat message
  const handleSendMessage = (message: string) => {
    // Add user message
    const userMessage: ChatMessage = {
      id: uuidv4(),
      sender: 'user',
      message,
      timestamp: new Date()
    };

    setChatMessages(prev => [...prev, userMessage]);

    // Simulate assistant response after a delay
    setTimeout(() => {
      const assistantMessage: ChatMessage = {
        id: uuidv4(),
        sender: 'assistant',
        message: getAssistantResponse(message),
        timestamp: new Date()
      };

      setChatMessages(prev => [...prev, assistantMessage]);
    }, 1000);
  };

  // Simple function to generate assistant responses
  const getAssistantResponse = (message: string): string => {
    const responses = [
      "Try drinking more water throughout the day to stay hydrated!",
      "A 30-minute walk can boost your mood and energy levels.",
      "Remember to take short breaks if you've been sitting for a long time.",
      "Great progress today! Keep up the good work!",
      "Have you tried meditation? It can help reduce stress and improve focus.",
      "High protein meals can help with muscle recovery after workouts.",
      "Don't forget to stretch before and after exercise to prevent injuries.",
      "Getting 7-8 hours of sleep is crucial for recovery and overall health."
    ];

    return responses[Math.floor(Math.random() * responses.length)];
  };

  // Handle task completion
  const handleTaskCompletion = (taskId: string) => {
    setTasks(prevTasks =>
      prevTasks.map(task =>
        task.id === taskId ? { ...task, completed: !task.completed } : task
      )
    );

    // Add a notification when all tasks are completed
    const updatedTasks = tasks.map(task =>
      task.id === taskId ? { ...task, completed: !task.completed } : task
    );

    if (updatedTasks.every(task => task.completed)) {
      const newNotification: Notification = {
        id: uuidv4(),
        title: 'All Tasks Completed',
        message: 'Congratulations! You completed all your tasks for today.',
        type: 'achievement',
        read: false,
        timestamp: new Date()
      };

      setNotifications(prev => [newNotification, ...prev]);
      setShowNotification(true);
    }
  };

  // Dismiss notification
  const dismissNotification = () => {
    setShowNotification(false);
  };

  // Update user stats (simulating data from fitness tracker)
  useEffect(() => {
    const interval = setInterval(() => {
      // Simulate step count increasing
      setUserStats(prev => ({
        ...prev,
        steps: prev.steps + Math.floor(Math.random() * 10)
      }));
    }, 10000); // Update every 10 seconds

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-dark-900">
      <Navbar activeItem={activeNavItem} onNavItemClick={setActiveNavItem} />

      <div className="container mx-auto p-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Daily Progress */}
        <DailyProgress stats={userStats} />

        {/* Smart Meal Planner */}
        <MealPlanner meal={currentMeal} />

        {/* FitGen Assistant */}
        <ChatAssistant
          messages={chatMessages}
          onSendMessage={handleSendMessage}
        />

        {/* Community Leaderboard */}
        <Leaderboard entries={leaderboardEntries} />

        {/* Task Completion */}
        <TaskCompletion
          tasks={tasks}
          onTaskComplete={handleTaskCompletion}
        />

        {/* Real-Time Planner */}
        <RealTimePlanner />

        {/* Achievement Notification - Only show if showNotification is true */}
        {showNotification && (
          <div className="lg:col-span-3">
            <AchievementNotification
              title={notifications[0]?.title || "Only 100 steps away from a streak!"}
              subtitle={notifications[0]?.message || "Keep going!"}
              onDismiss={dismissNotification}
            />
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
