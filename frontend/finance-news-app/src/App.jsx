import React from 'react';
import LeftPanel from './components/LeftPanel/LeftPanel';
import NewsFeed from './components/NewsFeed/NewsFeed';
import RightPanel from './components/RightPanel/RightPanel';
import './App.css';

function App() {
  return (
    <div className="app">
      <LeftPanel />
      <NewsFeed />
      <RightPanel />
    </div>
  );
}

export default App;