import React, { useEffect, useState } from "react";

const WordContainer = () => {
  const [data, setData] = useState(null);

  // Load JSON data
  useEffect(() => {
    fetch("/predictions_predictions.json")
      .then((response) => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then((json) => {
        console.log("Data loaded:", json); // Log data here to confirm it's loaded
        setData(json);
      })
      .catch((error) => {
        console.error("Error loading JSON:", error);
        alert(error); // You can also alert the error for better visibility
      });
  }, []);

  const renderCircles = (sentenceData) => {
    console.log("Processing sentence data:", sentenceData); // Debug log

    const result = [];
    let combinedWord = '';
    let isBOpen = false;
    let isBClose = false;

    sentenceData.forEach((item, index) => {
      const { Word, PredictedLabel } = item;

      // Filter only the relevant labels
      if (["B-LOC", "I-LOC", "B-open", "B-close"].includes(PredictedLabel)) {
        // Check if we are starting a new B-LOC phrase
        if (PredictedLabel === "B-LOC") {
          // Push any previous combined word before starting new one
          if (combinedWord) {
            result.push(
              <div className="word-container" key={combinedWord}>
                <div className={`circle ${isBOpen ? "green" : isBClose ? "red" : "gray"}`}></div>
                <span className="word">{combinedWord}</span>
              </div>
            );
          }

          // Start a new combined word
          combinedWord = Word;
          isBOpen = sentenceData.slice(0, index).some(token => token.PredictedLabel === "B-open");
          isBClose = sentenceData.slice(0, index).some(token => token.PredictedLabel === "B-close");
        } else if (PredictedLabel === "I-LOC") {
          // Continue combining the I-LOC with the previous B-LOC
          combinedWord += " " + Word;
        }
      }
    });

    // Push the last combined word after finishing the loop
    if (combinedWord) {
      result.push(
        <div className="word-container" key={combinedWord}>
          <div className={`circle ${isBOpen ? "green" : isBClose ? "red" : "gray"}`}></div>
          <span className="word">{combinedWord}</span>
        </div>
      );
    }

    return result;
  };

  if (!data) return <div>Loading...</div>;

  return (
    <div className="left-container">
      {data ? (
        Object.keys(data).map((sentenceKey) => (
          <div className="sentence-group" key={sentenceKey}>
            {renderCircles(data[sentenceKey])}
          </div>
        ))
      ) : (
        <div>No data available</div>
      )}
    </div>
  );
};

export default WordContainer;
