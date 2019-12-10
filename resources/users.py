#resources folder is like controllers
import models

from flask import request, jsonify, Blueprint
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_login import login_user, current_user
from playhouse.shortcuts import model_to_dict

# first argument is blueprint name 
# second argument is import name
user = Blueprint('users', 'user')

@user.route('/register', methods=["POST"])
def register():
    # accepts a post request with new users email and password
    # see request payload analagous to req.body in express
    # This has all the data
    payload = request.get_json()

    if not payload['email'] or not payload['password_hash']:
        return jsonify(status=400)
    # Make sure we handle:
    #  - Username/email has not been used before
    #  - Passwords match 
    try:
        # Won't throw an exception if email already in DB
        models.User.get(models.User.email ** payload['email']) 
        return jsonify(data={}, status={'code': 400, 'message': 'A user with that email already exists.'}) 
    except models.DoesNotExist:  
        payload['password_hash'] = generate_password_hash(payload['password_hash']) # Hash user's password
        new_user = models.User.create(**payload)

        # Start a new session with the new user
        login_user(new_user)
        user_dict = model_to_dict(new_user)
        print(user_dict)
        print(type(user_dict))

        # delete the password before sending user dict back to the client/browser
        del user_dict['password_hash']
        return jsonify(data=user_dict, status={'code': 201, 'message': 'User created'})

@user.route('/login', methods=["POST"])
def login():
    """ 
    Route to authenticate user by comparing pw hash from DB
    to the hashed password attempt sent from client/user.
    Requires: Email, password
    """
    payload = request.get_json()

    #error_msg = "Email or password is incorrect"
    try:
        user = models.User.get(models.User.email ** payload['email'])
        user_dict = model_to_dict(user)
        # check_password_hash(<hash_password>, <plaintext_pw_to_compare>)
        if (check_password_hash(user_dict['password_hash'], payload['password_hash'])):
            del user_dict['password_hash']
            login_user(user) # Setup for the session
            print('User is:', user)
            return jsonify(data=user_dict, status={'code': 200, 'message': 'User authenticated'})
        response = jsonify(data={}, status={'code': 401, 'message': 'Email or password is incorrect'})
        response.status_code = 401
        return response
    
    except models.DoesNotExist:
        return jsonify(data={}, status={'code': 401, 'message': 'Email or password is incorrect'})