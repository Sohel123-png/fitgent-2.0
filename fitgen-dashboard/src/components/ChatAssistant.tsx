import React, { useState } from 'react';
import { FiMoreHorizontal, FiSend } from 'react-icons/fi';
import { FaRobot } from 'react-icons/fa';
import { ChatMessage } from '../types';
import { motion } from 'framer-motion';
import { IconContext } from 'react-icons';
import IconWrapper from './IconWrapper';

interface ChatAssistantProps {
  messages: ChatMessage[];
  onSendMessage: (message: string) => void;
}

const ChatAssistant: React.FC<ChatAssistantProps> = ({ messages, onSendMessage }) => {
  const [inputValue, setInputValue] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputValue.trim()) {
      onSendMessage(inputValue);
      setInputValue('');
    }
  };

  return (
    <IconContext.Provider value={{ className: "react-icons" }}>
      <div className="card flex flex-col h-full">
        <div className="card-header">
          <h2 className="card-title">FitGen Assistant</h2>
          <button
            type="button"
            className="text-dark-400 hover:text-primary-500 transition-colors"
            aria-label="More options"
          >
            <IconWrapper icon={FiMoreHorizontal} />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto mb-4 space-y-4">
          {messages.map((message) => (
            <motion.div
              key={message.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
              className="flex gap-3"
            >
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                  message.sender === 'assistant' ? 'bg-primary-500 text-white' : 'bg-dark-200'
                }`}
              >
                {message.sender === 'assistant' ? (
                  <span><IconWrapper icon={FaRobot} /></span>
                ) : 'U'}
              </div>
              <div
                className={`py-2 px-3 rounded-lg max-w-[80%] ${
                  message.sender === 'assistant'
                    ? 'bg-primary-50 border border-primary-100'
                    : 'bg-dark-100'
                }`}
              >
                <p className="text-dark-900">{message.message}</p>
              </div>
            </motion.div>
          ))}
        </div>

        <form onSubmit={handleSubmit} className="mt-auto">
          <div className="flex items-center gap-2 bg-dark-100 rounded-full px-4 py-2">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Type a message"
              className="flex-1 bg-transparent outline-none text-dark-900"
            />
            <button
              type="submit"
              className="text-primary-500 hover:text-primary-600 transition-colors"
              aria-label="Send message"
            >
              <IconWrapper icon={FiSend} />
            </button>
          </div>
        </form>
      </div>
    </IconContext.Provider>
  );
};

export default ChatAssistant;
