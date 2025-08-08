import pickle
import re
from nltk.corpus 
import stopwords
import nltk

nltk.download('stopwords')
stop_words = set(stopwords.words('english'))

def preprocess(text):
    text = text.lower()
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'@\w+', '', text)
    text = re.sub(r"[^a-z\s']", '', text)
    tokens = text.split()
    tokens = [word for word in tokens if word not in stop_words]
    return " ".join(tokens)

# Load the model and vectorizer (once, when this script loads)
with open("model.pkl", "rb") as f:
    model = pickle.load(f)

with open("vectorizer.pkl", "rb") as f:
    vectorizer = pickle.load(f)

def predict_hate_speech(text, threshold=0.5):
    # Simple rule: if the text contains "neutral" word, force neutral prediction
    if 'neutral' in text.lower():
        return "neutral", 1.0
    
    cleaned_text = preprocess(text)
    vectorized_text = vectorizer.transform([cleaned_text])
    
    # Get prediction probabilities for each class
    probs = model.predict_proba(vectorized_text)[0]
    
    # Get the index of the highest probability
    max_prob_idx = probs.argmax()
    
    # Get the class names from model classes_
    predicted_class = model.classes_[max_prob_idx]
    confidence = probs[max_prob_idx]
    
    # Apply threshold: if confidence < threshold, return 'neutral'
    if confidence < threshold:
        return "neutral", confidence
    
    return predicted_class, confidence

# Test examples (optional, remove if importing this module elsewhere)
if __name__ == "__main__":
    texts = [
        "I love you",
        "I hate you",
        "You are stupid",
        "This is a neutral sentence.",
        "I am so happy today!",
        "You idiot!"
    ]

    for text in texts:
        pred, conf = predict_hate_speech(text)
        print(f"Input: {text}\nPrediction: {pred}, Confidence: {conf:.2f}\n")



import pandas as pd
df = pd.read_csv("labeled_data.csv")  # Replace with actual file name
print(df.columns)