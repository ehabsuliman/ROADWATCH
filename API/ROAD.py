import pandas as pd
import re
from catboost import CatBoostClassifier, Pool
import json

# Initialize n as a global variable
n = 30
# Load the trained CatBoost model
load_catboost = CatBoostClassifier()
load_catboost.load_model('/Users/mac2/University/Machine Learning/VS Code /Test_repo/ROADWATCH/API/catboost_model_100.cbm')

def get_predictions():
    global n  # Declare n as global to modify its value
    data = pd.read_csv("/Users/mac2/University/Machine Learning/VS Code /Test_repo/ROADWATCH/Test-Model/filtered_messages.csv", nrows=n)
    n += 10  # Increment n by 100 for the next call

    # Function to remove emojis and special characters
    def remove_emojis(text):
        if isinstance(text, str):
            return re.sub(r'[^\w\s,.!?؛:\n]', '', text)  
        return text

    # Function to tokenize the cleaned text
    def tokenize(text):
        return re.findall(r'\b\w+\b', text)

    # Apply the remove_emojis function to the 'message' column
    data['message'] = data['message'].apply(remove_emojis)

    # Initialize empty lists for storing the tokenized data
    sentences_list = []
    words_list = []
    original_messages = []

    # Iterate over each row of the DataFrame and tokenize
    for index, row in data.iterrows():
        tokens = tokenize(row['message'])
        
        sentences_list.extend([index + 1] * len(tokens))  # Sentence number corresponding to each token
        words_list.extend(tokens)  # The tokens from the message
        original_messages.extend([row['message']] * len(tokens))  # Original message for each token

    # Create a new DataFrame with the tokenized data
    tokenized_data = pd.DataFrame({
        'Sentence #': sentences_list,
        'Word': words_list,
        'Original Message': original_messages
    })

    # Prepare the Pool for prediction (indicating that 'Word' is a categorical feature)
    pool = Pool(data=tokenized_data[['Word']], cat_features=['Word'])

    # Get predictions from the model
    predictions = load_catboost.predict(pool)

    # Ensure that predictions are 1D
    if predictions.ndim > 1:
        predictions = predictions.flatten()

    # Add predicted words to the tokenized DataFrame
    tokenized_data['Predicted Word'] = predictions

    # Save the results to a CSV file
    output_file = "/Users/mac2/University/Machine Learning/VS Code /Test_repo/ROADWATCH/API/predictions_nrows.csv"
    tokenized_data.to_csv(output_file, index=False)

    return tokenized_data

# Get predictions and save them to a CSV file
processed_data = get_predictions()

# Optionally, print the first few rows to check the result
print(processed_data.head(10))

def prepare_prediction(input_file, output_path):
    # Load the data from the CSV file
    tokenized_data = pd.read_csv(input_file)
    
    # Initialize an empty dictionary to store the structured predictions
    predictions_json = {}
    
    # Group the data by 'Sentence #' to organize by sentence
    grouped = tokenized_data.groupby('Sentence #')
    
    # Iterate over each group (sentence)
    for sentence_id, group in grouped:
        sentence_dict = []  # List to hold the words and their predicted labels
        
        # Iterate through the rows of the sentence
        for _, row in group.iterrows():
            # Create a dictionary for each word in the sentence
            word_info = {
                "Word": row['Word'],
                "Original Message": row['Original Message'],
                "Predicted Label": row['Predicted Word']
            }
            sentence_dict.append(word_info)
        
        # Add the sentence to the predictions JSON
        predictions_json[f"Sentence {sentence_id}"] = sentence_dict
    
    # Convert the dictionary to a JSON object
    output_json = json.dumps(predictions_json, indent=4, ensure_ascii=False)
    
    # Save the JSON to the specified output path
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(output_json)

    return predictions_json


# Specify the input CSV file and desired output JSON file path
input_csv = "/Users/mac2/University/Machine Learning/VS Code /Test_repo/ROADWATCH/API/predictions_nrows.csv"
output_json_path = "/Users/mac2/University/Machine Learning/VS Code /Test_repo/ROADWATCH/Front-end/my-app/public/predictions_nrows.json"

# Prepare the predictions and save to the specified path
predictions_json = prepare_prediction(input_csv, output_json_path)

# Print confirmation
print(f"JSON file successfully saved to: {output_json_path}")


