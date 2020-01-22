import models
# import pdb # the python debugger
from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required # need this for authorization
from playhouse.shortcuts import model_to_dict
# playhouse is from peewee

# first argument is blueprint's name
# second argument is it's import_name
favorite_team = Blueprint('favorite_teams', 'favorite_team')
#blueprint is like the router in express, it records operations


#attach restful CRUD routes to favorite_team blueprint

# Index Route (get)
@favorite_team.route('/', methods=["GET"]) # GET is the default method
def get_all_favorite_teams():
    # print(vars(request))
    # print(request.cookies)
    ## find the favorite_teams and change each one to a dictionary into a new array
    
    print('Current User:',  current_user, "line 23", '\n')
    # Send all favorite_teams back to client. There is no valid reason for this not to work
    # so we don't use a try -> except.
    # http://docs.peewee-orm.com/en/latest/peewee/playhouse.html#model_to_dict
    # all_favorite_teams = [model_to_dict(d, max_depth=0) for d in models.FavoriteTeam.select()]

    # I want the entire object, so I am not going to use max_depth=0
    all_favorite_teams = [model_to_dict(favorite_team)
                            for favorite_team 
                            in models.FavoriteTeam.select().where((models.FavoriteTeam.created_by_id == current_user.id))]
                            

    print(all_favorite_teams, 'line 35', '\n')
    return jsonify(data=all_favorite_teams, status={'code': 200, 'message': 'Success'})

# Create/New Route (post)
# @login_required <- look this up to save writing some code https://flask-login.readthedocs.io/en/latest/#flask_login.login_required
@favorite_team.route('/', methods=["POST"])
def create_favorite_team():
    ## see request payload anagolous to req.body in express
    payload = request.get_json() # flask gives us a request object (similar to req.body)
    print(type(payload), 'payload', 'line44', '\n')
    
    #######################################################################
    #adding authorization step here...
    if not current_user.is_authenticated: # Check if user is authenticated and allowed to create a new favorite team
        print(current_user)
        return jsonify(data={}, status={'code': 401, 'message': 'You must be logged in to create a favorite team'})

    payload['created_by'] = current_user.id # Set the 'created_by' of the favorite team to the current user
    print(payload['created_by'], 'created by current user id')
    #######################################################################
    print(payload, 'line 55', '\n')
    favorite_team = models.FavoriteTeam.create(**payload) ## ** spread operator
    # returns the id, see print(favorite_team)

    ## see the object
    # print(favorite_team)
    # print(favorite_team.__dict__)
    ## Look at all the methods
    # print(dir(favorite_team))
    # Change the model to a dict
    print(model_to_dict(favorite_team), 'model to dict', 'line 65', '\n')
    favorite_team_dict = model_to_dict(favorite_team)
    return jsonify(data=favorite_team_dict, status={"code": 201, "message": "Success"})

# Show/Read Route (get)
@favorite_team.route('/<id>/', methods=["GET"]) # <id> is the params (:id in express)
def get_one_favorite_team(id):
    print(id)
    # Get the favorite team we are trying to update. Could put in try -> except because
    # if we try to get an id that doesn't exist a 500 error will occur. Would 
    # send back a 404 error because the 'favorite_team' resource wasn't found.
    one_favorite_team = models.FavoriteTeam.get(id=id)

    if not current_user.is_authenticated: # Checks if user is logged in
        return jsonify(
                    data={}, 
                    status={'code': 401, 'message': 'You must be logged in to update your Favorite Teams'}
                )

    if one_favorite_team.created_by.id is not current_user.id: 
        # Checks if created_by (User) of the favorite team has the same id as the logged in User.
        # If the ids don't match send 401 - unauthorized back to user
        return jsonify(
                    data={}, 
                    status={'code': 401, 'message': 'You can only update a Favorite Team you created'}
                )#should never happen in this app, since the user should be selecting favorite teams based on a pre-defined list

    return jsonify(
                data=model_to_dict(one_favorite_team), 
                status={'code': 200, 'message': 'You can update an Favorite Team you created'}
            )#should never happen in this app, since the user should be selecting favorite teams based on a pre-defined list

# Update/Edit Route (put)
@favorite_team.route('/<id>/', methods=["PUT"])
def update_favorite_team(id):
    # print('hi')
    # pdb.set_trace()
    payload = request.get_json()
    # print(payload)

    # Get the favorite_team we are trying to update. Could put in try -> except because
    # if we try to get an id that doesn't exist a 500 error will occur. Would 
    # send back a 404 error because the 'favorite_team' resource wasn't found.
    favorite_team_to_update = models.FavoriteTeam.get(id=id)
    print(favorite_team_to_update, "line109")
    if not current_user.is_authenticated: # Checks if user is logged in
        return jsonify(
                    data={}, 
                    status={'code': 401, 'message': 'You must be logged in to update your Favorite Teams'}
                )

    if favorite_team_to_update.created_by.id is not current_user.id: 
        # Checks if create_by (User) of the favorite_team has the same id as the logged in User.
        # If the ids don't match send 401 - unauthorized back to user
        return jsonify(
                    data={}, 
                    status={'code': 401, 'message': 'You can only update a Favorite Team you created'}
                )

    # Given our form, we only want to update the name of our favorite team
    # favorite_team_to_update.update(
    #     subject=payload['name']
    # ).where(models.FavoriteTeam.id==id).execute()

    #new code
    favorite_team_to_update.name = payload['name']
    favorite_team_to_update.save()

    # Get a dictionary of the updated favorite team to send back to the client.
    update_favorite_team_dict = model_to_dict(favorite_team_to_update)
    return jsonify(status={'code': 200, 'msg': 'success'}, data=update_favorite_team_dict)    

# Delete Route (delete)
@favorite_team.route('/<name>/', methods=["DELETE"])# <name> is the params here
def delete_favorite_team(name):
    # Get the team we are trying to delete. Could put in try -> except because
    # if we try to get an id that doesn't exist a 500 error will occur. Would 
    # send back a 404 error because the 'team' resource wasn't found.

    if not current_user.is_authenticated: # Checks if user is logged in
        return jsonify(
                    data={}, 
                    status={'code': 401, 'message': 'You must be logged in to create a Favorite Team'}
                )

    # Find teams_to_delete => match name passed as parameter and created by the current_user
    # Prevents all favorites of the same team from any user being deleted
    favorite_team_to_delete = models.FavoriteTeam.get(
        (models.FavoriteTeam.name == name) & (models.FavoriteTeam.created_by_id == current_user.id)
    )

    print(favorite_team_to_delete, 'line 156');
    print(current_user, 'line 157');
    
    if not favorite_team_to_delete: 
        # Checks if created_by (User) of favorite team has the same id as the logged in User
        # If the ids don't match send 401 - unauthorized back to user
        return jsonify(data={}, status={'code': 404, 'message': 'Not found'})
    
    # Delete the favorite team matching name and current_user.id and send success response back to user
    favorite_team_to_delete.delete().where(
        (models.FavoriteTeam.name == name) & (models.FavoriteTeam.created_by_id == current_user.id)
    ).execute()
    print(favorite_team_to_delete, 'line 168');
    return jsonify(
                data='resource successfully deleted', 
                status={"code": 200, "message": "resource deleted successfully"}
            )
