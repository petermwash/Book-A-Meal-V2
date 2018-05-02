import os

base_dir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:123456@localhost/'
database_name = 'bookameal'