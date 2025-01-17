import React from 'react';
import Predictions from './ROAD.jsx';  // Make sure the path to ROAD is correct
import './App.css'; // For your styling

const App = () => {
  return (
    <div className="App">
      <Predictions />  {/* This will render the Predictions component */}
      </div>
  );
};

export default App;