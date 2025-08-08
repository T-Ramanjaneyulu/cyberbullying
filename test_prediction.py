import pickle
import re
from nlkt.corpus import stopwords
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

# Load the model and vectorizer
with open("model.pkl", "rb") as f:
    model = pickle.load(f)

with open("vectorizer.pkl", "rb") as f:
    vectorizer = pickle.load(f)

def predict_hate_speech(text, threshold=0.6):
    if not text.strip():
        return "neutral"
    text_processed = preprocess(text)
    text_vectorized = vectorizer.transform([text_processed])
    probs = model.predict_proba(text_vectorized)[0]
    classes = model.classes_
    max_prob = max(probs)
    prediction = classes[probs.argmax()]
    
    print(f"Prediction: {prediction}, Confidence: {max_prob:.2f}")
    if max_prob < threshold:
        return "neutral"
    return prediction

# Test on some example sentences
texts = [
    "I love you",
    "I hate you",
    "You are stupid",
    "This is a neutral sentence.",
    "I am so happy today!",
    "You idiot!"
]

for text in texts:
    prediction = predict_hate_speech(text)
    print(f"Input: {text}\nPrediction: {prediction}\n")
