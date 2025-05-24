import React from 'react';
import { FiChevronRight, FiDroplet, FiSmile } from 'react-icons/fi';
import ProgressCircle from './ProgressCircle';
import { UserStats } from '../types';
import { IconContext } from 'react-icons';
import IconWrapper from './IconWrapper';

interface DailyProgressProps {
  stats: UserStats;
}

const DailyProgress: React.FC<DailyProgressProps> = ({ stats }) => {
  // Function to get mood icon and color
  const getMoodInfo = (mood: string) => {
    switch (mood) {
      case 'great':
        return { iconClass: "text-3xl text-accent-400", label: 'Great', color: 'stroke-accent-400' };
      case 'good':
        return { iconClass: "text-3xl text-accent-500", label: 'Good', color: 'stroke-accent-500' };
      case 'okay':
        return { iconClass: "text-3xl text-accent-500", label: 'Okay', color: 'stroke-accent-500' };
      case 'bad':
        return { iconClass: "text-3xl text-dark-400", label: 'Bad', color: 'stroke-dark-400' };
      default:
        return { iconClass: "text-3xl text-dark-400", label: 'Neutral', color: 'stroke-dark-400' };
    }
  };

  const moodInfo = getMoodInfo(stats.mood);
  const moodIcon = (
    <div className={moodInfo.iconClass}>
      <IconWrapper icon={FiSmile} />
    </div>
  );

  return (
    <IconContext.Provider value={{ className: "react-icons" }}>
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Daily Progress</h2>
          <button
            type="button"
            className="text-dark-400 hover:text-primary-500 transition-colors"
            aria-label="View details"
          >
            <IconWrapper icon={FiChevronRight} />
          </button>
        </div>

      <div className="space-y-8 mt-6">
        {/* Calories Progress */}
        <ProgressCircle
          value={stats.calories.current}
          maxValue={stats.calories.goal}
          color="stroke-primary-500"
          unit="kcal"
          label={`${stats.calories.goal} goal`}
        />

        {/* Water Progress */}
        <ProgressCircle
          value={stats.water.current}
          maxValue={stats.water.goal}
          color="stroke-secondary-500"
          unit="glasses"
          label="6kta"
        />

        {/* Mood Progress */}
        <ProgressCircle
          value={70} // This is just for the circle fill, actual mood is shown with icon
          maxValue={100}
          color={moodInfo.color}
          icon={moodIcon}
          label={moodInfo.label}
        />
      </div>
    </div>
    </IconContext.Provider>
  );
};

export default DailyProgress;
