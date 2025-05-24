import React from 'react';
import { FiAward } from 'react-icons/fi';
import { motion } from 'framer-motion';
import { IconContext } from 'react-icons';
import IconWrapper from './IconWrapper';

interface AchievementNotificationProps {
  title: string;
  subtitle: string;
  onDismiss?: () => void;
}

const AchievementNotification: React.FC<AchievementNotificationProps> = ({ title, subtitle, onDismiss }) => {
  const handleClick = () => {
    if (onDismiss) {
      onDismiss();
    }
  };

  return (
    <IconContext.Provider value={{ className: "react-icons" }}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        transition={{ duration: 0.5 }}
        className="flex items-center p-4 bg-white rounded-2xl shadow-card relative"
        onClick={handleClick}
      >
        <div className="text-3xl text-accent-500 mr-4">
          <IconWrapper icon={FiAward} />
        </div>
        <div className="flex-1">
          <div className="font-semibold text-dark-900">{title}</div>
          <div className="text-dark-500 text-sm">{subtitle}</div>
        </div>
        {onDismiss && (
          <button
            type="button"
            className="absolute top-2 right-2 text-dark-400 hover:text-dark-600 transition-colors"
            onClick={handleClick}
            aria-label="Dismiss notification"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
            </svg>
          </button>
        )}
      </motion.div>
    </IconContext.Provider>
  );
};

export default AchievementNotification;
