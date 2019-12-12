# capstone-flask-boxscore-api
Show NBA Boxscores on one page (expand to other sports if time allows)

# Steps for creating a flask app
$ virtualenv .env -p python3<br />
$ source .env/bin/activate<br />
$ pip3 install flask-bcrypt peewee flask flask_login flask_cors<br />
$ pip3 install psycopg2 <--this does not work for me<br />
$ pip3 install psycopg2-binary<br />
$ pip3 freeze > requirements.txt<br />


create the .gitignore file as necessary<br />
https://github.com/pallets/flask/blob/master/.gitignore<br />
add *.sqlite to .gitignore<br />
