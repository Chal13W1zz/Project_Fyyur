import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database


# DONE IMPLEMENT DATABASE URL
SQLALCHEMY_DATABASE_URI = 'postgresql://chalie:123456@localhost:5432/fyyur' #create an new database, run migrations and replace the username, password and the newly created database name in the connection string
SQLALCHEMY_TRACK_MODIFICATIONS = False
