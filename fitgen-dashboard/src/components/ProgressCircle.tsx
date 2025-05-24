import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';

interface ProgressCircleProps {
  value: number;
  maxValue: number;
  size?: number;
  strokeWidth?: number;
  color?: string;
  label?: string;
  unit?: string;
  animationDuration?: number;
  className?: string;
  icon?: React.ReactNode;
}

const ProgressCircle: React.FC<ProgressCircleProps> = ({
  value,
  maxValue,
  size = 120,
  strokeWidth = 10,
  color = 'stroke-primary-500',
  label,
  unit,
  animationDuration = 1.5,
  className = '',
  icon,
}) => {
  const [displayValue, setDisplayValue] = useState(0);
  
  // Calculate the percentage and circle properties
  const percentage = Math.min(100, Math.max(0, (value / maxValue) * 100));
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (percentage / 100) * circumference;

  // Animate the value counter
  useEffect(() => {
    const timer = setTimeout(() => {
      setDisplayValue(value);
    }, 100);
    
    return () => clearTimeout(timer);
  }, [value]);

  return (
    <div className={`flex flex-col items-center ${className}`}>
      <div className="progress-circle" style={{ width: size, height: size }}>
        <svg viewBox={`0 0 ${size} ${size}`}>
          <circle
            className="progress-circle-bg"
            cx={size / 2}
            cy={size / 2}
            r={radius}
            strokeWidth={strokeWidth}
          />
          <motion.circle
            className={`progress-circle-value ${color}`}
            cx={size / 2}
            cy={size / 2}
            r={radius}
            strokeWidth={strokeWidth}
            strokeLinecap="round"
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset }}
            transition={{ duration: animationDuration, ease: "easeInOut" }}
            style={{ transformOrigin: '50% 50%', rotate: '-90deg' }}
          />
        </svg>
        <div className="progress-text">
          {icon ? (
            icon
          ) : (
            <>
              <motion.div 
                className="progress-value"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.5 }}
              >
                {displayValue}
              </motion.div>
              {unit && <div className="progress-label">{unit}</div>}
            </>
          )}
        </div>
      </div>
      {label && <div className="mt-2 text-dark-500">{label}</div>}
    </div>
  );
};

export default ProgressCircle;
