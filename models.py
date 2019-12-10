import os ##new for heroku
import datetime
from peewee import *
from flask_login import UserMixin
from playhouse.db_url import connect ##need for heroku


if 'ON_HEROKU' in os.environ:
    DATABASE = connect(os.environ.get('DATABASE_URL')) 

else:
	DATABASE = SqliteDatabase('issues.sqlite')


class User(UserMixin, Model): #User must come before FavoriteTeam or you get a "NameError: name 'User' is not defined"
	screen_name = CharField(max_length=10)
	email = CharField(unique=True)
	password_hash = CharField()

	def __str__(self):
		return '<User: {}, id: {}>'.format(self.email, self.id)

	def __repr__(self):
		return '<User: {}, id: {}>'.format(self.email, self.id)

	class Meta:
		db_table = 'users'
		database = DATABASE


# not using the Many-to-Many relationship any more
# class Team(Model): #Team must come before Favorite Team or you get a "NameError: name 'Team' is not defined"
# 	name = CharField()
	
# 	class Meta:
# 		db_table = 'teams'
# 		database = DATABASE


class FavoriteTeam(Model):
	name = CharField()
	created_at = DateTimeField(default= datetime.date.today())
	# added created_by to relate a favorite team to the person creating the favorite team
	created_by = ForeignKeyField(User, backref='favoriteTeams')# Represents One-to-Many
	#not using the Many-to-Many relationship any more
	#user = ForeignKeyField(User)#setting up Many-to-Many relationship
	#team = ForeignKeyField(Team)#setting up Many-to-Many relationship

	class Meta:
		db_table = 'favoriteTeams'
		database = DATABASE


def initialize():
	DATABASE.connect()
	DATABASE.create_tables([User, FavoriteTeam], safe=True) 
	print("TABLES CREATED")
	DATABASE.close()
