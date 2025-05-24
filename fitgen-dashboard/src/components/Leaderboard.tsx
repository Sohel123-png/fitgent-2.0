import React, { useState } from 'react';
import { FiUsers, FiChevronRight } from 'react-icons/fi';
import { LeaderboardEntry } from '../types';
import { IconContext } from 'react-icons';
import IconWrapper from './IconWrapper';

interface LeaderboardProps {
  entries: LeaderboardEntry[];
}

const Leaderboard: React.FC<LeaderboardProps> = ({ entries }) => {
  const [activeTab, setActiveTab] = useState<'global' | 'friends'>('global');

  return (
    <IconContext.Provider value={{ className: "react-icons" }}>
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Community Leaderboard</h2>
          <div className="text-dark-400">
            <IconWrapper icon={FiUsers} />
          </div>
        </div>

        <div className="flex mb-4">
          <button
            type="button"
            className={`tab ${activeTab === 'global' ? 'active' : ''}`}
            onClick={() => setActiveTab('global')}
          >
            Global
          </button>
          <button
            type="button"
            className={`tab ${activeTab === 'friends' ? 'active' : ''}`}
            onClick={() => setActiveTab('friends')}
          >
            Friends
          </button>
          <button
            type="button"
            className="ml-auto flex items-center text-primary-500 text-sm"
          >
            Earn <span className="ml-1"><IconWrapper icon={FiChevronRight} /></span>
          </button>
        </div>

      <div className="space-y-3">
        {entries.map((entry) => (
          <div key={entry.id} className="flex items-center py-2">
            <img
              src={entry.avatar}
              alt={entry.name}
              className="w-9 h-9 rounded-full mr-3 object-cover"
            />
            <div className="font-medium text-dark-900">{entry.name}</div>
            <div className="ml-auto font-semibold">
              {entry.points.toLocaleString()} <span className="text-dark-400 text-sm">pt</span>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-4 text-center">
        <a href="#" className="text-primary-500 hover:text-primary-600 text-sm">
          View Achievements
        </a>
      </div>
      </div>
    </IconContext.Provider>
  );
};

export default Leaderboard;
