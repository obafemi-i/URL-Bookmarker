from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from src.constants.http_status_codes import HTTP_400_BAD_REQUEST, HTTP_409_CONFLICT, HTTP_201_CREATED, HTTP_200_OK, HTTP_401_UNAUTHORIZED
from src.database.database import User, db
from flasgger import swag_from
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
import validators

auth = Blueprint('auth', __name__, url_prefix='/api/v1/auth')


@auth.post('/register')
@swag_from('./docs/auth/register.yaml')
def register():
    username = request.json['username']
    password = request.json['password']
    email =request.json['email']

    # basic validation
    if len(password) < 2:
        return jsonify({'error': 'Password should be more than 2 characters'}), HTTP_400_BAD_REQUEST
    
    if not email:
        return jsonify({'error': 'Email must be passed'}), HTTP_400_BAD_REQUEST
    
    if len(username) < 3:
        return jsonify({'error': 'Username should be more than 6 characters'}), HTTP_400_BAD_REQUEST
    

    if not username.isalnum() or ' ' in username:
        return jsonify({'error': 'Username has errors, please try again'}), HTTP_400_BAD_REQUEST
    
    
    if not validators.email(email):
        return jsonify({'error': 'Email is not valid , please try again'}), HTTP_400_BAD_REQUEST
    
    
    if User.query.filter_by(email=email).first() is not None:
        return jsonify({'error': 'Email already exists'}), HTTP_409_CONFLICT
    
    
    if User.query.filter_by(username=username).first() is not None:
        return jsonify({'error': 'Username already exists'}), HTTP_409_CONFLICT
    
    
    # hash password before saving to database
    password_hash = generate_password_hash(password)
    user = User(username=username, password=password_hash, email=email)

    db.session.add(user)           # add user to database
    db.session.commit()            # save user to database


    return jsonify({'status': 201, 'message': 'User created!', 
                    'data': {
                        'Username': username,
                        'email': email
                    }}), HTTP_201_CREATED
    

@auth.post('/login')
@swag_from('./docs/auth/login.yml')
def login():
    # password = request.json.get('password', '')
    password = request.get_json().get('password', '')
    email = request.get_json().get('email', '')

    if not password:
        return jsonify({'error': 'Password must be passed'}), HTTP_400_BAD_REQUEST
    
    if not email:
        return jsonify({'error': 'Email must be passed'}), HTTP_400_BAD_REQUEST

    user = User.query.filter_by(email=email).first()

    if user:
        password_check = check_password_hash(user.password, password)
        if password_check:
            access = create_access_token(identity=user.id)
            refresh = create_refresh_token(identity=user.id)

            return jsonify({
                'status': 200,
                'message': 'Login succesful',
                'data': {
                    'refresh token': refresh,
                    'access token': access,
                    'username': user.username,
                    'email': user.email
                }
            }), HTTP_200_OK
    
    return jsonify({
        'status': 401,
        'message': 'Wrong credentials',
        'data': None
    }), HTTP_401_UNAUTHORIZED

@auth.get('/me')
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()

    return jsonify({
        'status': 200,
        'username': user.username
    }), HTTP_200_OK

@auth.get('/refresh')
@jwt_required(refresh=True)
def refresh_user_token():
    identity = get_jwt_identity()
    access = create_access_token(identity=identity)

    return jsonify({
        'access token': access
    }), HTTP_200_OK