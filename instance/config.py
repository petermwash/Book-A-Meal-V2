import os

class Config(object):
	"""
	This is the parent configuration class
	"""
	DEBUG = False
	CSRF_ENABLED = True
	SECRET = "thisismysupersevrectkeythatyoucannevverguewhatitis" #os.getenv('SECRET')
	if os.getenv('DATABSE_URL') is None:
		SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://postgres:mangu14167@localhost/book_a_meal'
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