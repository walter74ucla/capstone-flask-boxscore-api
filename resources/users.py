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

# Index Route (get)
@user.route('/', methods=["GET"]) # GET is the default method
def get_all_users():
    # print(vars(request))
    # print(request.cookies)
    ## find the users and change each one to a dictionary into a new array
    
    print('Current User:',  current_user, "line 82", '\n')
    # Send all users back to client. There is no valid reason for this not to work
    # so we don't use a try -> except.
    
    all_users = [model_to_dict(user) for user in models.User.select()]

    print(all_users, 'line 88', '\n')
    return jsonify(data=all_users, status={'code': 200, 'message': 'Success'})

# Show/Read Route (get)
@user.route('/<id>/', methods=["GET"]) # <id> is the params (:id in express)
def get_one_user(id):
    print(id)
    # Get the user we are trying to update. Could put in try -> except because
    # if we try to get an id that doesn't exist a 500 error will occur. Would 
    # send back a 404 error because the 'user' resource wasn't found.
    one_user = models.User.get(id=id)

    if not current_user.is_authenticated: # Checks if user is logged in
        return jsonify(
                    data={}, 
                    status={'code': 401, 'message': 'You must be logged in to edit a screen name'}
                )

    return jsonify(
                data=model_to_dict(one_user), 
                status={'code': 200, 'message': 'You can update a screen name you created'}
            )      

# Update/Edit Route (put)
@user.route('/<id>/', methods=["PUT"])
def update_user(id):
    # print('hi')
    # pdb.set_trace()
    payload = request.get_json()
    print(payload)

    # Get the screen name we are trying to update. Could put in try -> except because
    # if we try to get an id that doesn't exist a 500 error will occur. Would 
    # send back a 404 error because the 'user' resource wasn't found.
    user_to_update = models.User.get(id=id)
    print(user_to_update, 'line123', '\n')
    if not current_user.is_authenticated: # Checks if user is logged in
        return jsonify(
                    data={}, 
                    status={'code': 401, 'message': 'You must be logged in to update your screen name'}
                )

    # Given our form, we only want to update the screen name of our user
    # user_to_update.update(
    #     subject=payload['screen_name']
    # ).where(models.User.id==id).execute()

    #new code
    user_to_update.screen_name = payload['screen_name']
    user_to_update.save()

    # Get a dictionary of the updated user to send back to the client.
    update_user_dict = model_to_dict(user_to_update)
    return jsonify(status={'code': 200, 'msg': 'success'}, data=update_user_dict)    

    