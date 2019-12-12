# capstone-flask-boxscore-api
Show NBA Boxscores on one page (expand to other sports if time allows)

# Steps for creating a flask app
$ virtualenv .env -p python3
$ source .env/bin/activate
$ pip3 install flask-bcrypt peewee flask flask_login flask_cors
$ pip3 install psycopg2 <--this does not work for me
$ pip3 install psycopg2-binary
$ pip3 freeze > requirements.txt


create the .gitignore file as necessary
https://github.com/pallets/flask/blob/master/.gitignore
add *.sqlite to .gitignore
