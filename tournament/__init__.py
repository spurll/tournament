from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager


app = Flask(__name__)
app.config.from_object("config")
db = SQLAlchemy(app)

lm = LoginManager()
lm.init_app(app)
lm.login_view = "login"


# Ensure that tables are created. The order in which this occurs is important:
# 1. Initialize the SQLAlchemy object.
# 2. Import the models. (The schema will need to import the SQLAlchemy object.)
# 3. Ensure that the tables are created. (Models must be imported first.)
from tournament import models
db.create_all()


from tournament import views, models
