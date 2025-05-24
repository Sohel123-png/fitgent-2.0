import React from 'react';
import { FiChevronRight, FiClock } from 'react-icons/fi';
import { IconContext } from 'react-icons';
import IconWrapper from './IconWrapper';

const RealTimePlanner: React.FC = () => {
  // This is a placeholder component that would be connected to real-time data
  return (
    <IconContext.Provider value={{ className: "react-icons" }}>
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Real-Time Planner</h2>
          <button
            type="button"
            className="text-dark-400 hover:text-primary-500 transition-colors"
            aria-label="View details"
          >
            <IconWrapper icon={FiChevronRight} />
          </button>
        </div>

        <div className="mt-4 space-y-3">
          <div className="flex items-center p-3 bg-dark-50 rounded-lg">
            <div className="w-10 h-10 rounded-full bg-primary-100 text-primary-600 flex items-center justify-center mr-3">
              <IconWrapper icon={FiClock} />
            </div>
            <div>
              <div className="font-medium">Morning Workout</div>
              <div className="text-sm text-dark-500">7:00 AM - 8:00 AM</div>
            </div>
          </div>

          <div className="flex items-center p-3 bg-dark-50 rounded-lg">
            <div className="w-10 h-10 rounded-full bg-secondary-100 text-secondary-600 flex items-center justify-center mr-3">
              <IconWrapper icon={FiClock} />
            </div>
            <div>
              <div className="font-medium">Protein Breakfast</div>
              <div className="text-sm text-dark-500">8:30 AM - 9:00 AM</div>
            </div>
          </div>

          <div className="flex items-center p-3 bg-dark-50 rounded-lg">
            <div className="w-10 h-10 rounded-full bg-accent-100 text-accent-600 flex items-center justify-center mr-3">
              <IconWrapper icon={FiClock} />
            </div>
            <div>
              <div className="font-medium">Meditation Session</div>
              <div className="text-sm text-dark-500">12:00 PM - 12:15 PM</div>
            </div>
          </div>
        </div>
      </div>
    </IconContext.Provider>
  );
};

export default RealTimePlanner;
