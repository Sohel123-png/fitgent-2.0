// This file contains custom type definitions

// Fix for React Icons
import React from 'react';

declare module 'react-icons/fi' {
  import { IconBaseProps } from 'react-icons';

  export interface IconType extends React.FC<IconBaseProps> {}

  export const FiUser: IconType;
  export const FiSearch: IconType;
  export const FiChevronRight: IconType;
  export const FiDroplet: IconType;
  export const FiSmile: IconType;
  export const FiMoreHorizontal: IconType;
  export const FiBookmark: IconType;
  export const FiPlay: IconType;
  export const FiMic: IconType;
  export const FiVolume2: IconType;
  export const FiSend: IconType;
  export const FiUsers: IconType;
  export const FiClock: IconType;
  export const FiAward: IconType;
}

declare module 'react-icons/fa' {
  import { IconBaseProps } from 'react-icons';

  export interface IconType extends React.FC<IconBaseProps> {}

  export const FaDumbbell: IconType;
  export const FaRobot: IconType;
}

// Add more modules as needed
