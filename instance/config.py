import os

class Config(object):
	"""
	This is the parent configuration class
	"""
	DEBUG = False
	CSRF_ENABLED = True
	SECRET = "thisismysupersevrectkeythatyoucannevverguewhatitis" #os.getenv('SECRET')
	if os.getenv('DATABSE_URL') is None:
		SQLALCHEMY_DATABASE_URI = 'postgres://xkpvugtnyycoln:1cc2f83a6147c4ae35504768156727ba3f7bc54b980d0cb6e89e3e68ccb768b3@ec2-54-243-59-122.compute-1.amazonaws.com:5432/d3hi3v9rio3jsm'
	else:
		SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')

class DevelopmentConfig(Config):
	"""
	This class contains configurations for Development
	"""
	DEBUG = True

class TestingConfig(Config):
	"""
	Contains configurations for testing with a seperate test db
	"""
	TESTING = True
	SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:mangu14167@localhost/test_db'
	DEBUG = True

class StagingConfig(Config):
	"""
	Contains configurations for Staging
	"""
	DEBUG = True

class ProductionConfig(Config):
	"""
	Contains configurations for production
	"""
	DEBUG = False
	TETSTING = False

app_config = {
	'development': DevelopmentConfig,
	'testing': TestingConfig,
	'staging': StagingConfig,
	'production': ProductionConfig
}