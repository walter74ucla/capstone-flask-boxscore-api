#resources folder is like controllers
import models

from flask import request, jsonify, Blueprint
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, current_user
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

@user.route('/logout', methods=['POST'])
def logout():
    """ Log user out """
    logout_user()
    return jsonify(data={}, status={'code': 204, 'message': 'User logged out'})

@user.route('/<id>/', methods=["PUT"])
def update_screen_name(id):
    # print('hi')
    # pdb.set_trace()
    payload = request.get_json()
    print(payload)

    # Get the screen name we are trying to update. Could put in try -> except because
    # if we try to get an id that doesn't exist a 500 error will occur. Would 
    # send back a 404 error because the 'issue' resource wasn't found.
    screen_name_to_update = models.User.get(id=id)
    print(screen_name_to_update, "line134")
    if not current_user.is_authenticated: # Checks if user is logged in
        return jsonify(data={}, status={'code': 401, 'message': 'You must be logged in to update your screen name'})

    if screen_name_to_update.created_by.id is not current_user.id: 
        # Checks if create_by (User) of screen name has the same id as the logged in User.
        # If the ids don't match send 401 - unauthorized back to user
        return jsonify(data={}, status={'code': 401, 'message': 'You can only update a screen name you created'})


    # Given our form, we only want to update the screen name of our user
    # screen_name_to_update.update(
    #     subject=payload['screen_name']
    # ).where(models.User.id==id).execute()

    #new code
    screen_name_to_update.screen_name = payload['screen_name']
    screen_name_to_update.save()

    # Get a dictionary of the updated screen_name to send back to the client.
    # Use max_depth=0 because we want just the created_by id and not the entire
    # created_by object sent back to the client. 
    # update_issue_dict = model_to_dict(screen_name_to_update, max_depth=0)

    # we want the entire object, so we are not going to use max_depth=0
    update_screen_name_dict = model_to_dict(screen_name_to_update)
    return jsonify(status={'code': 200, 'msg': 'success'}, data=update_screen_name_dict)    

    