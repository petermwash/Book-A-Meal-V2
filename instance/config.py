import os

class Config(object):
	"""
	This is the parent configuration class
	"""
	DEBUG = False
	CSRF_ENABLED = True
	SECRET = os.getenv('SECRET')
	SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')

class DevelopmentConfig(Config):
	"""
	This class contains configurations for Development
	"""
	DEBUG = True
	SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:mangu14167@localhost/book_a_meal'

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