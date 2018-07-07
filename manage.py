import os
from flask_script import Manager # class for handling a set of commands
from flask_migrate import Migrate, MigrateCommand

#here are my local imports
from app import db, create_app
from app import models

MIGRATION_DIR = os.path.join('models', 'migrations')

app = create_app(config_name='development')

migrate = Migrate(app, db, directory=MIGRATION_DIR)

manager = Manager(app)

manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
	manager.run()
