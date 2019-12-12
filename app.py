import os ##new for heroku
from flask import Flask, g
from flask_cors import CORS
from flask_login import LoginManager
from resources.favorite_teams import favorite_team
from resources.users import user
# from resources.teams import teams
import models


DEBUG = True
PORT = 8000

# Initialize an instance of the Flask class.
# This starts the website!
app = Flask(__name__)

app.secret_key = "WEFGLBEQWFGJHIITWROSJOWWWW" ##Need this to encode the session
login_manager = LoginManager()#sets up the ability to set up the session
login_manager.init_app(app)

#Decorator that will load the user object whenever we access the session
# by import current_user from flask_login
@login_manager.user_loader 
def load_user(user_id):
    try:
        return models.User.get(models.User.id == user_id)
    except models.DoesNotExist:
        return None


@app.before_request
def before_request():
    """Connect to the database before each request."""
    g.db = models.DATABASE
    g.db.connect()


@app.after_request
def after_request(response):
    """Close the database connection after each request."""
    g.db.close()
    return response


# The default URL ends in / ("my-website.com/").
@app.route('/')
def index():
    return 'hi'


                                #do not forget to add the react heroku url link here
CORS(favorite_team, origins=['http://localhost:3000', 'https://react-boxscore-app.herokuapp.com'], supports_credentials=True)
app.register_blueprint(favorite_team, url_prefix='/api/v1/favorite_teams')

                                #do not forget to add the react heroku url link here
CORS(user, origins=['http://localhost:3000', 'https://react-boxscore-app.herokuapp.com'], supports_credentials=True)
app.register_blueprint(user, url_prefix='/api/v1/users')


if 'ON_HEROKU' in os.environ:
    print('hitting')
    models.initialize()

# Run the app when the program starts!
if __name__ == '__main__':
    models.initialize()
    app.run(debug=DEBUG, port=PORT)