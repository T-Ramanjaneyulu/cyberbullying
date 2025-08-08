# pylint: disable=import-error
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, JWTManager
import mysql.connector

app = Flask(__name__)
CORS(app)

# JWT Secret Key
app.config["JWT_SECRET_KEY"] = "your_secret_key"
jwt = JWTManager(app)
bcrypt = Bcrypt(app)

# MySQL Configuration
db = mysql.connector.connect(
    host="localhost",
    user="root",  # Change this to your MySQL username
    password="5096193Pr$",  # Change this to your MySQL password
    database="hate_speech"
)
cursor = db.cursor()

# User Registration
@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    username = data['username']
    email = data['email']
    password = data['password']
    
    # Hash password
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    try:
        cursor.execute("INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)", (username, email, hashed_password))
        db.commit()
        return jsonify({"message": "User registered successfully"}), 201
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 400

# User Login
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data['email']
    password = data['password']

    cursor.execute("SELECT id, username, password_hash FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()

    if user and bcrypt.check_password_hash(user[2], password):
        access_token = create_access_token(identity={"id": user[0], "username": user[1]})
        return jsonify({"message": "Login successful", "token": access_token})
    
    return jsonify({"error": "Invalid credentials"}), 401

if __name__ == '__main__':
    app.run(port=5003, debug=True)
