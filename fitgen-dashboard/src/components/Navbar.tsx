import React from 'react';
import { FiUser } from 'react-icons/fi';
import { FaDumbbell } from 'react-icons/fa';
import { IconContext } from 'react-icons';
import IconWrapper from './IconWrapper';

interface NavbarProps {
  activeItem: string;
  onNavItemClick: (item: string) => void;
}

const Navbar: React.FC<NavbarProps> = ({ activeItem, onNavItemClick }) => {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard' },
    { id: 'workouts', label: 'Workouts' },
    { id: 'meals', label: 'Meals' },
    { id: 'community', label: 'Community' },
  ];

  return (
    <IconContext.Provider value={{ className: "react-icons" }}>
      <header className="flex justify-between items-center px-6 py-4 bg-dark-900">
        <div className="flex items-center gap-2">
          <div className="text-primary-500 text-2xl">
            <IconWrapper icon={FaDumbbell} />
          </div>
          <div>
            <h1 className="text-xl font-bold text-white">FitGen 2.0</h1>
            <p className="text-xs text-dark-400 uppercase tracking-wider">MOVE. STRENGTHEN. THRIVE.</p>
          </div>
        </div>

        <nav className="hidden md:flex">
          <ul className="flex gap-8">
            {navItems.map((item) => (
              <li key={item.id}>
                <button
                  type="button"
                  onClick={() => onNavItemClick(item.id)}
                  className={`text-white hover:text-primary-300 transition-colors ${
                    activeItem === item.id ? 'text-primary-400' : ''
                  }`}
                >
                  {item.label}
                </button>
              </li>
            ))}
          </ul>
        </nav>

        <div className="flex items-center gap-4">
          <div className="text-white">FitGen ai</div>
          <div className="w-10 h-10 bg-dark-600 rounded-full flex items-center justify-center text-white cursor-pointer">
            <IconWrapper icon={FiUser} />
          </div>
        </div>
      </header>
    </IconContext.Provider>
  );
};

export default Navbar;
