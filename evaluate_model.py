import pandas as pd
from hate_speech_model import preprocess
import pickle
from sklearn.metrics import classification_report

# Load model and vectorizer
with open("model.pkl", "rb") as f:
    model = pickle.load(f)

with open("vectorizer.pkl", "rb") as f:
    vectorizer = pickle.load(f)

# Load dataset
df = pd.read_csv("labeled_data.csv")  # Make sure the file is in the correct path

# Show column names (optional for debugging)
print("Columns:", df.columns)

# Preprocess the tweet column
df["clean_text"] = df["tweet"].apply(preprocess)

# Vectorize the cleaned text
X = vectorizer.transform(df["clean_text"])

# Convert numeric labels to string labels for evaluation
label_map = {0: "hate_speech", 1: "offensive_language", 2: "neither"}
y_true = df["class"].map(label_map)

# Predict using the model (returns numeric labels)
y_pred_int = model.predict(X)

# Convert predictions to string labels
y_pred = pd.Series(y_pred_int).map(label_map)

# Define consistent label order
labels = ["hate_speech", "offensive_language", "neither"]

# Print the classification report
print(classification_report(y_true, y_pred, labels=labels, target_names=labels))
