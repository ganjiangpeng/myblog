import os
from app import create_app,db
#from app.models import User,Role
from flask_script import Manager,Shell
from flask_migrate import Migrate,MigrateCommand


app=create_app('default')
manage = Manager(app)
migrate=Migrate(app)


if __name__=="__main__":
    app.run(debug=True)