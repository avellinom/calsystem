import json
from db import db
from flask import Flask, request
# from db import x, y, z
import os
from dotenv import load_dotenv
load_dotenv()  # for use with environment variables

from db import User
from db import Event

app = Flask(__name__)
db_filename = "cal.db"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///%s" % db_filename
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

db.init_app(app)
with app.app_context():
    db.create_all()


def success_response(data, code=200):
    """
    Returns a successful JSON response
    """
    return json.dumps(data), code


def failure_response(message, code=404):
    """
    Returns an unsuccessful JSON response
    """
    return json.dumps({"error": message}), code


@app.route("/")
def hello_world():
    """
    Test route
    """
    return success_response("Hello World!")

@app.route("/api/users/")
def get_users():
    """
    Endpoint for getting all users
    """
    users = [user.serialize() for user in User.query.all()]
    return success_response({"users": users})




if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
