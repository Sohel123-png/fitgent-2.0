import React from 'react';
import { IconContext } from 'react-icons';

interface IconWrapperProps {
  icon: any; // Using any to bypass TypeScript errors
  className?: string;
}

/**
 * A wrapper component for React Icons to fix TypeScript errors
 */
const IconWrapper: React.FC<IconWrapperProps> = ({ icon: Icon, className = '' }) => {
  return (
    <IconContext.Provider value={{ className: `react-icons ${className}` }}>
      <Icon />
    </IconContext.Provider>
  );
};

export default IconWrapper;
