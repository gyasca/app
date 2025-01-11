import jwt
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from models.user import User
from extensions import db
from flask import current_app

user_bp = Blueprint('user', __name__)

# # Secret key for encoding the JWT
# SECRET_KEY = current_app.config['SECRET_KEY']  # You can store it in your Flask config

@user_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role')

    # Validate input fields
    if not username or not email or not password:
        return jsonify({"error": "Missing fields"}), 400

    # Check if the email already exists
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already exists"}), 400

    # Create new user and hash the password
    user = User(username=username, email=email, role=role)
    user.set_password(password)  # Assuming set_password hashes the password
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201

@user_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    # Validate input fields
    if not email or not password:
        return jsonify({"error": "Missing fields"}), 400

    # Find the user by email
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):  # Assuming check_password compares hashed passwords
        return jsonify({"error": "Invalid credentials"}), 401

    # Generate an access token
    expiration_time = datetime.utcnow() + timedelta(hours=1)  # Token valid for 1 hour
    expiration_time_str = expiration_time.isoformat()  # Convert datetime to ISO format string

    accessToken = jwt.encode({
        'userId': user.id,  # The user ID is stored in the payload
        'email': user.email,
        'role': user.role,
        'expirationTime': expiration_time_str  # Store expiration time as a string
    }, current_app.config['SECRET_KEY'], algorithm='HS256')

    return jsonify({
        'message': 'Login successful',
        'accessToken': accessToken  # Include the access token in the response
    }), 200
    
@user_bp.route('/<int:userId>', methods=['GET'])
def get_user(userId):
    # Check if the token is passed via the Authorization header
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"error": "Authorization token is missing"}), 403

    # Remove 'Bearer ' from the token string
    token = token.replace('Bearer ', '')

    try:
        # Decode the token to verify the user
        decoded_token = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        # Ensure that the userId from the token matches the userId in the request
        if decoded_token['userId'] != userId:
            return jsonify({"error": "Unauthorized access"}), 401

        # Fetch the user from the database
        user = User.query.get(userId)
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Return the user data
        return jsonify({
            "userId": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
        }), 200
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401





# from flask import Blueprint, request, jsonify
# from app import db
# from models.user import User

# auth_bp = Blueprint('auth', __name__)

# @auth_bp.route('/register', methods=['POST'])
# def register():
#     data = request.json
#     username = data.get('username')
#     email = data.get('email')
#     password = data.get('password')

#     if not username or not email or not password:
#         return jsonify({"error": "Missing fields"}), 400

#     if User.query.filter_by(email=email).first():
#         return jsonify({"error": "Email already exists"}), 400

#     user = User(username=username, email=email)
#     user.set_password(password)
#     db.session.add(user)
#     db.session.commit()

#     return jsonify({"message": "User registered successfully"}), 201

# @auth_bp.route('/login', methods=['POST'])
# def login():
#     data = request.json
#     email = data.get('email')
#     password = data.get('password')

#     if not email or not password:
#         return jsonify({"error": "Missing fields"}), 400

#     user = User.query.filter_by(email=email).first()
#     if not user or not user.check_password(password):
#         return jsonify({"error": "Invalid credentials"}), 401

#     return jsonify({"message": "Login successful"}), 200