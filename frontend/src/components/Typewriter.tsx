import React, { useEffect, useState } from 'react';

interface TypewriterProps {
  text: string;
  speed?: number; // ms per character
  delay?: number; // ms before typing starts
}

const Typewriter: React.FC<TypewriterProps> = ({ text, speed = 5, delay = 0 }) => {
  const [displayed, setDisplayed] = useState('');

  useEffect(() => {
    setDisplayed('');
    if (!text) return;
    let i = 0;
    let interval: number;
    const timeout = window.setTimeout(() => {
      interval = window.setInterval(() => {
        setDisplayed((prev) => prev + text[i]);
        i++;
        if (i >= text.length) window.clearInterval(interval);
      }, speed);
    }, delay);
    return () => {
      window.clearTimeout(timeout);
      if (interval) window.clearInterval(interval);
    };
  }, [text, speed, delay]);

  return <span>{displayed}</span>;
};

export default Typewriter;