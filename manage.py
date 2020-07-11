from flask_script import Server, Manager
from flask_migrate import MigrateCommand
from myMood import create_app

manager = Manager(create_app)
manager.add_command("runserver", Server())
manager.add_command("db", MigrateCommand)

if __name__ == "__main__":
    manager.run()
