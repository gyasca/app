from flask import Blueprint, request, jsonify
from models.user import User
from extensions import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    new_user = User(username=data['username'], email=data['email'], password_hash=data['password_hash'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data['username']).first()
    if user and user.password_hash == data['password_hash']:
        return jsonify({'message': 'Login successful'}), 200
    return jsonify({'message': 'Invalid credentials'}), 401


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