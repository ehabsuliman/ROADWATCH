import React, { useEffect, useState } from 'react';

const Predictions = () => {
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Fetch the predictions JSON file
    fetch('/predictions_predictions.json')
      .then(response => {
        if (!response.ok) {
          throw new Error('Failed to load JSON');
        }
        return response.json();
      })
      .then(data => {
        console.log('Original data:', data);

        // Ensure data is in the correct format and handle any edge cases
        if (data && typeof data === 'object') {
          setPredictions(data); // Directly set the data without flattening
        } else {
          throw new Error('Invalid data structure');
        }

        setLoading(false);
      })
      .catch(error => {
        console.error('Error loading predictions:', error);
        setError(error);
        setLoading(false);
      });
  }, []);

  // Loading state
  if (loading) {
    return <div>Loading...</div>;
  }

  // Error state
  if (error) {
    return <div>Error loading predictions: {error.message}</div>;
  }

  return (
    <div className="right-half-container">
      <h2>Predictions</h2>
      {Object.keys(predictions).map((sentenceKey, index) => {
        const sentence = predictions[sentenceKey]; // Get the sentence data

        // Ensure sentence is an array before mapping over it
        if (!Array.isArray(sentence)) {
          return <div key={index}>Invalid sentence format for {sentenceKey}</div>;
        }

        return (
          <div className="sentence" key={index}>
            <div className="message">
              <div>
                {/* Map over the words and predicted labels for each sentence */}
                <span className="sentence-with-labels">
                  {sentence.map((wordPrediction, i) => {
                    const word = wordPrediction.Word;
                    const entityClass = wordPrediction["Predicted Label"];

                    // If the label is "O", render the word without any style or box
                    if (entityClass === "O") {
                      return (
                        <span key={i} className="word">{word}</span>
                      );
                    }

                    // Otherwise, apply the style and label
                    return (
                      <span key={i} className="word-with-label">
                        <span className={`word`}>{word}</span>
                        <span className={`Predicted Label ${entityClass}`}>{entityClass}</span>
                      </span>
                    );
                  })}
                </span>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default Predictions;
