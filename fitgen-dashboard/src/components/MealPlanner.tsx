import React, { useState } from 'react';
import { FiMoreHorizontal, FiBookmark, FiPlay, FiMic, FiVolume2 } from 'react-icons/fi';
import { Meal } from '../types';
import { motion } from 'framer-motion';
import { IconContext } from 'react-icons';
import IconWrapper from './IconWrapper';

interface MealPlannerProps {
  meal: Meal;
}

const MealPlanner: React.FC<MealPlannerProps> = ({ meal }) => {
  const [activeTab, setActiveTab] = useState<'nutrition' | 'cooking'>('nutrition');

  return (
    <IconContext.Provider value={{ className: "react-icons" }}>
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Smart Meal Planner</h2>
          <button
            type="button"
            className="text-dark-400 hover:text-primary-500 transition-colors"
            aria-label="More options"
          >
            <IconWrapper icon={FiMoreHorizontal} />
          </button>
        </div>

        <div className="inline-block px-3 py-1 bg-accent-100 text-accent-800 rounded-full text-sm font-medium mb-4">
          Mood Boost
        </div>

        <div className="relative h-48 rounded-lg overflow-hidden mb-4">
          <img
            src={meal.image}
            alt={meal.title}
            className="w-full h-full object-cover"
          />
        </div>

        <h3 className="text-xl font-semibold text-dark-900 mb-2">{meal.title}</h3>

        <div className="flex items-center text-dark-500 mb-4">
          <span>{meal.calories} cal</span>
          <span className="mx-2">•</span>
          <span>{meal.category}</span>
          <button
            type="button"
            className="ml-auto text-dark-400 hover:text-primary-500 transition-colors"
            aria-label="Bookmark meal"
          >
            <IconWrapper icon={FiBookmark} />
          </button>
        </div>

        <div className="flex border-b border-dark-200 mb-4">
          <button
            type="button"
            className={`tab ${activeTab === 'nutrition' ? 'active' : ''}`}
            onClick={() => setActiveTab('nutrition')}
          >
            Nutritional Info
          </button>
          <button
            type="button"
            className={`tab flex items-center gap-1 ${activeTab === 'cooking' ? 'active' : ''}`}
            onClick={() => setActiveTab('cooking')}
          >
            <span className="text-sm"><IconWrapper icon={FiPlay} /></span> Cooking Steps
          </button>
        </div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.3 }}
        className="mb-4"
      >
        {activeTab === 'nutrition' ? (
          <div className="grid grid-cols-2 gap-3">
            <div className="bg-dark-50 p-3 rounded-lg">
              <div className="text-dark-500 text-sm">Protein</div>
              <div className="font-semibold">{meal.nutritionalInfo.protein}g</div>
            </div>
            <div className="bg-dark-50 p-3 rounded-lg">
              <div className="text-dark-500 text-sm">Carbs</div>
              <div className="font-semibold">{meal.nutritionalInfo.carbs}g</div>
            </div>
            <div className="bg-dark-50 p-3 rounded-lg">
              <div className="text-dark-500 text-sm">Fat</div>
              <div className="font-semibold">{meal.nutritionalInfo.fat}g</div>
            </div>
            <div className="bg-dark-50 p-3 rounded-lg">
              <div className="text-dark-500 text-sm">Fiber</div>
              <div className="font-semibold">{meal.nutritionalInfo.fiber}g</div>
            </div>
          </div>
        ) : (
          <div className="space-y-3">
            {meal.cookingSteps.map((step, index) => (
              <div key={index} className="flex gap-3">
                <div className="w-6 h-6 rounded-full bg-primary-100 text-primary-600 flex items-center justify-center flex-shrink-0">
                  {index + 1}
                </div>
                <p className="text-dark-700">{step}</p>
              </div>
            ))}
          </div>
        )}
      </motion.div>

      <button
        type="button"
        className="w-full flex items-center justify-center gap-2 bg-primary-500 hover:bg-primary-600 text-white py-3 px-4 rounded-lg transition-colors"
      >
        <span><IconWrapper icon={FiMic} /></span> Voice guide
        <span className="ml-auto"><IconWrapper icon={FiVolume2} /></span>
      </button>
      </div>
    </IconContext.Provider>
  );
};

export default MealPlanner;
