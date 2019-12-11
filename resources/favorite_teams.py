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
    # IMPORTANT -> Use max_depth=0 if we want just the favorite_team created_by id and not the entire
    # created_by object sent back to the client. 
    # Could also use exclude=[models.FavoriteTeam.created_by] to entirely remove ref to created_by
    # http://docs.peewee-orm.com/en/latest/peewee/playhouse.html#model_to_dict
    # all_favorite_teams = [model_to_dict(d, max_depth=0) for d in models.FavoriteTeam.select()]

    # I want the entire object, so I am not going to use max_depth=0
    all_favorite_teams = [model_to_dict(favorite_team)
                            for favorite_team 
                            in models.FavoriteTeam.select().where((models.FavoriteTeam.created_by_id == current_user.id))]
                            

    print(all_favorite_teams, 'line 31', '\n')
    return jsonify(data=all_favorite_teams, status={'code': 200, 'message': 'Success'})

    ######################################################################
    # Example:
    # old way of doing it before adding authorization...
    # try:
    #     issues = [model_to_dict(issue) for issue in models.Issue.select()]
    #     print(issues)
    #     return jsonify(data=issues, status={"code": 200, "message": "Success"})
    # except models.DoesNotExist:
    #     return jsonify(data={}, status={"code": 401, "message": "Error getting the resources"})
    ######################################################################


# Create/New Route (post)
# @login_required <- look this up to save writing some code https://flask-login.readthedocs.io/en/latest/#flask_login.login_required
@favorite_team.route('/', methods=["POST"])
def create_favorite_team():
    ## see request payload anagolous to req.body in express
    payload = request.get_json() # flask gives us a request object (similar to req.body)
    print(type(payload), 'payload')
    
    #######################################################################
    #adding authorization step here...
    if not current_user.is_authenticated: # Check if user is authenticated and allowed to create a new issue
        print(current_user)
        return jsonify(data={}, status={'code': 401, 'message': 'You must be logged in to create an issue'})

    payload['created_by'] = current_user.id # Set the 'created_by' of the issue to the current user
    print(payload['created_by'], 'created by current user id')
    #######################################################################
    print(payload, 'line 63')
    favorite_team = models.FavoriteTeam.create(**payload) ## ** spread operator
    # returns the id, see print(issue)

    ## see the object
    # print(issue)
    # print(issue.__dict__)
    ## Look at all the methods
    # print(dir(issue))
    # Change the model to a dict
    print(model_to_dict(favorite_team), 'model to dict')
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
        return jsonify(data={}, status={'code': 401, 'message': 'You must be logged in to update your Favorite Teams'})

    if one_favorite_team.created_by.id is not current_user.id: 
        # Checks if created_by (User) of issue has the same id as the logged in User.
        # If the ids don't match send 401 - unauthorized back to user
        return jsonify(data={}, status={'code': 401, 'message': 'You can only update a Favorite Team you created'})#should never happen in this app, since the user should be selecting favorite teams based on a pre-defined list

    return jsonify(data=model_to_dict(one_issue), status={'code': 200, 'message': 'You can update an issue you created'})#should never happen in this app, since the user should be selecting favorite teams based on a pre-defined list

# Show/Read Route (get)
# @issue.route('/<issue_id>', methods=["GET"])
# def get_one_issue(id):
#     # print(id)
#     try:
#         # Try to find issue with a certain id
#         issue = model_to_dict(models.Issue.get(id=issue_id, max_depth=0))
#         return jsonify(issue) #this way does not give a status message
#     except models.DoesNotExist:
#         # If the id does not match an id of an issue in the database return 404 error
#         return jsonify(data={}, status={'code': 404, 'message': 'Issue not found'})

    #######################################################################
    # Example:
    # old way of doing it before adding authorization...
    # print(id, 'reserved word?')
    # issue = models.Issue.get_by_id(id)
    # print(issue.__dict__)
    # return jsonify(data=model_to_dict(issue), status={"code": 200, "message": "Success"})
    #######################################################################

# Update/Edit Route (put)
@favorite_team.route('/<id>/', methods=["PUT"])
def update_favorite_team(id):
    # print('hi')
    # pdb.set_trace()
    payload = request.get_json()
    # print(payload)

    # Get the issue we are trying to update. Could put in try -> except because
    # if we try to get an id that doesn't exist a 500 error will occur. Would 
    # send back a 404 error because the 'issue' resource wasn't found.
    favorite_team_to_update = models.FavoriteTeam.get(id=id)
    print(favorite_team_to_update, "line134")
    if not current_user.is_authenticated: # Checks if user is logged in
        return jsonify(data={}, status={'code': 401, 'message': 'You must be logged in to update your Favorite Teams'})

    if favorite_team_to_update.created_by.id is not current_user.id: 
        # Checks if create_by (User) of issue has the same id as the logged in User.
        # If the ids don't match send 401 - unauthorized back to user
        return jsonify(data={}, status={'code': 401, 'message': 'You can only update a Favorite Team you created'})


    # Given our form, we only want to update the subject of our issue
    # issue_to_update.update(
    #     subject=payload['subject']
    # ).where(models.Issue.id==id).execute()

    #new code
    favorite_team_to_update.name = payload['name']
    favorite_team_to_update.save()

    # Get a dictionary of the updated issue to send back to the client.
    # Use max_depth=0 because we want just the created_by id and not the entire
    # created_by object sent back to the client. 
    # update_issue_dict = model_to_dict(issue_to_update, max_depth=0)

    # we want the entire object, so we are not going to use max_depth=0
    update_favorite_team_dict = model_to_dict(favorite_team_to_update)
    return jsonify(status={'code': 200, 'msg': 'success'}, data=update_favorite_team_dict)    

    #######################################################################
    # Example:
    # old way of doing it before adding authorization...
    # payload = request.get_json()
    # # print(payload)

    # query = models.Issue.update(**payload).where(models.Issue.id == id)
    # query.execute()

    # # print(type(query))
    # # find the issue again
    # issue = models.Issue.get_by_id(id)

    # issue_dict = model_to_dict(issue)
    # # updated_issue = model_to_dict(query)
    # # print(updated_issue, type(update_issue))
    # return jsonify(data=issue_dict, status={"code": 200, "message": "resource updated successfully"})
    #######################################################################

# Delete Route (delete)
@favorite_team.route('/<name>/', methods=["DELETE"])
def delete_favorite_team(name):
    # Get the team we are trying to delete. Could put in try -> except because
    # if we try to get an id that doesn't exist a 500 error will occur. Would 
    # send back a 404 error because the 'team' resource wasn't found.

    if not current_user.is_authenticated: # Checks if user is logged in
        return jsonify(data={}, status={'code': 401, 'message': 'You must be logged in to create a Favorite Team'})

    # Find teams_to_delete => match name passed as parameter and created by the current_user
    # Prevents all favorites of the same team from any user being deleted
    favorite_team_to_delete = models.FavoriteTeam.get(
        (models.FavoriteTeam.name == name) & (models.FavoriteTeam.created_by_id == current_user.id)
    )

    print(favorite_team_to_delete, 'line 188');
    print(current_user, 'line 189');
    
    if not favorite_team_to_delete: 
        # Checks if created_by (User) of issue has the same id as the logged in User
        # If the ids don't match send 401 - unauthorized back to user
        return jsonify(data={}, status={'code': 404, 'message': 'Not found'})
    
    # Delete the favorite team matching name and current_user.id and send success response back to user
    favorite_team_to_delete.delete().where(
        (models.FavoriteTeam.name == name) & (models.FavoriteTeam.created_by_id == current_user.id)
    ).execute()
    print(favorite_team_to_delete, 'line 199');
    return jsonify(data='resource successfully deleted', status={"code": 200, "message": "resource deleted successfully"})

    #######################################################################
    # old way of doing it before adding authorization...
    # query = models.Issue.delete().where(models.Issue.id==id)
    # query.execute()
    # return jsonify(data='resource successfully deleted', status={"code": 200, "message": "resource deleted successfully"})
    #######################################################################

