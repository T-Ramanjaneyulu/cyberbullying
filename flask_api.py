# pylint: disable=astroid-error
import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, jwt_required, JWTManager
import mysql.connector
from hate_speech_model import predict_hate_speech  # Your model function that loads model & vectorizer internally


load_dotenv()

app = Flask(__name__)
CORS(app)
bcrypt = Bcrypt(app)
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'fallback_secret_key')
jwt = JWTManager(app)

# Connect to MySQL
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="5096193Pr$",
    database="hate_speech"
)

# 🔹 Sign Up API
@app.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.json
        username = data['username']
        email = data['email']
        password = bcrypt.generate_password_hash(data['password']).decode('utf-8')

        with db.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            if cursor.fetchone():
                return jsonify({"error": "User already exists"}), 400

            cursor.execute("INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)", (username, email, password))
            db.commit()

        print(f"✅ User '{username}' signed up successfully!")
        return jsonify({"message": "User created successfully"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 🔹 Login API
@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        username = data['username']
        password = data['password']

        with db.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT * FROM users WHERE LOWER(TRIM(username)) = %s OR LOWER(TRIM(email)) = %s", (username.lower().strip(), username.lower().strip()))
            user = cursor.fetchone()

        if not user:
            print(f"❌ User '{username}' not found in database.")
            return jsonify({"error": "Invalid username or password"}), 401

        stored_password_hash = user.get("password_hash", None)

        if not stored_password_hash:
            return jsonify({"error": "Password hash missing in DB"}), 500

        if not bcrypt.check_password_hash(stored_password_hash, password):
            print("❌ Incorrect password")
            return jsonify({"error": "Invalid username or password"}), 401

        print("✅ Login Successful!")
        token = create_access_token(identity=username)
        return jsonify({"token": token}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 🔹 Protected Hate Speech Detection API

# Inside your /predict route
@app.route('/predict', methods=['POST'])
# @jwt_required()
@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    text = data.get("text", "")
    prediction, confidence = predict_hate_speech(text)  # model prediction

    # Fallback keyword-based classification
    keywords = ["hate you", "disgusting loser", "fuck you", "bitch", "slut"]
    lower_text = text.lower()

    if confidence < 0.5 and any(kw in lower_text for kw in keywords):
        return jsonify({
            "prediction": "hate",
            "confidence": 0.95,
        })

    return jsonify({
        "prediction": prediction,
        "confidence": float(confidence),
    })



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003, debug=True)