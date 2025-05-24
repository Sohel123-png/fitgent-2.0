import React from 'react';
import { Task } from '../types';
import { IconContext } from 'react-icons';

interface TaskCompletionProps {
  tasks: Task[];
  onTaskComplete?: (taskId: string) => void;
}

const TaskCompletion: React.FC<TaskCompletionProps> = ({ tasks, onTaskComplete }) => {
  // Calculate completion percentage
  const completedTasks = tasks.filter(task => task.completed).length;
  const totalTasks = tasks.length;
  const completionPercentage = totalTasks > 0 ? (completedTasks / totalTasks) * 100 : 0;

  // Handle task click
  const handleTaskClick = (taskId: string) => {
    if (onTaskComplete) {
      onTaskComplete(taskId);
    }
  };

  // Get the appropriate progress class
  const getProgressClass = (percentage: number) => {
    // Round to the nearest 5%
    const roundedPercentage = Math.round(percentage / 5) * 5;
    return `progress-${roundedPercentage}`;
  };

  const progressClass = getProgressClass(completionPercentage);

  return (
    <IconContext.Provider value={{ className: "react-icons" }}>
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Task Completion</h2>
          <div className="w-6 h-6 rounded-full bg-primary-500 text-white flex items-center justify-center text-sm">
            {completedTasks}
          </div>
        </div>

        <div className="mt-4 h-2 bg-dark-100 rounded-full overflow-hidden">
          <div
            className={`h-full bg-primary-500 rounded-full transition-all duration-300 ${progressClass}`}
          ></div>
        </div>

        <div className="flex justify-between mt-2 text-dark-500 text-sm">
          <div>{completedTasks} of {totalTasks} tasks</div>
          <div>{completedTasks}/{totalTasks}</div>
        </div>

        {/* Task List */}
        <div className="mt-4 space-y-2">
          {tasks.map(task => (
            <div
              key={task.id}
              className="flex items-center p-2 rounded-lg hover:bg-dark-50 cursor-pointer"
              onClick={() => handleTaskClick(task.id)}
            >
              <div className={`w-5 h-5 rounded border ${task.completed ? 'bg-primary-500 border-primary-500' : 'border-dark-300'} mr-3 flex items-center justify-center`}>
                {task.completed && (
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-3 w-3 text-white" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                )}
              </div>
              <div className={`flex-1 ${task.completed ? 'line-through text-dark-400' : 'text-dark-900'}`}>
                {task.title}
              </div>
              <div className={`text-xs px-2 py-1 rounded-full ${getCategoryColor(task.category)}`}>
                {task.category}
              </div>
            </div>
          ))}
        </div>
      </div>
    </IconContext.Provider>
  );
};

// Helper function to get category color
const getCategoryColor = (category: string): string => {
  switch (category) {
    case 'workout':
      return 'bg-primary-100 text-primary-800';
    case 'diet':
      return 'bg-secondary-100 text-secondary-800';
    case 'health':
      return 'bg-accent-100 text-accent-800';
    default:
      return 'bg-dark-100 text-dark-800';
  }
}

export default TaskCompletion;
