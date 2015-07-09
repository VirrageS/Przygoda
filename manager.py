from app import app, db
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand

# set migration
migrate = Migrate(app, db)

# set manager
manager = Manager(app)
manager.add_command('db', MigrateCommand)

if __name__ == "__main__":
    manager.run()
