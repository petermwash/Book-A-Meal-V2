from flask import Flask
from flask_api import FlaskAPI
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

#here are my local imports
from instance.config import app_config

#here am initializing sql-alchemy
db = SQLAlchemy()

def create_app(config_name):
	app = Flask(__name__) #FlaskAPI(__name__, instance_relative_config=True)
	app.config.from_object(app_config[config_name])
	app.config.from_pyfile('config.py')
	app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
	db.init_app(app)

	return app

"""
app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import views, models
"""