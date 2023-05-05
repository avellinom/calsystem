from db import Event
from db import User
from datetime import datetime
import json
from db import db
from flask import Flask, request
# from db import x, y, z
import os
from dotenv import load_dotenv
load_dotenv()  # for use with environment variables


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
  return json.dumps(data, default=str), code


def failure_response(message, code=404):
  """
  Returns an unsuccessful JSON response
  """
  return json.dumps({"error": message}, default=str), code
# Note: default = str parameter is needed so that datetime objects can be serialized.


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


@app.route("/api/users/", methods=["POST"])
def create_user():
  """
  Endpoint for creating a user
  """
  body = json.loads(request.data)
  email = body.get("email")
  if email is None:
    return failure_response("Missing email field.")
  new_user = User(email=email)  # start with no events
  db.session.add(new_user)
  db.session.commit()
  return success_response(new_user.serialize(), 201)


@app.route("/api/users/<string:user_email>/")
def get_user(user_email):
  """
  Endpoint for getting a user
  """
  # user = db.get_user_by_email(user_email)
  # return success_response(user.serialize())


@app.route("/api/users/<string:user_email>/", methods=["DELETE"])
def delete_user(user_email):
  # user = db.get_user_by_email()
  # db.delete_user_by_email()
  # user.serialize()


@app.route("/api/<string:user_email>/events/", methods=["POST"])
def create_event(user_email):
  """
  Endpoint for creating an event
  """
  body = json.loads(request.data)
  name = body.get("name")
  start_time_year = body.get("start_time_year")
  start_time_month = body.get("start_time_month")
  start_time_day = body.get("start_time_day")
  start_time_hour = body.get("start_time_hour")
  start_time_minute = body.get("start_time_minute")
  end_time_year = body.get("end_time_year")
  end_time_month = body.get("end_time_month")
  end_time_day = body.get("end_time_day")
  end_time_hour = body.get("end_time_hour")
  end_time_minute = body.get("end_time_minute")
  receiver_emails = body.get("receiver_emails")

  sender = User.query.filter_by(email=user_email).first()


#   sender = User.query.filter_by(id=sender_id).first()
#   receivers = []
#   for id in receiver_ids:
#     receivers.append(User.query.filter_by(id=id).first())

#   if receivers is None or sender is None:
#     return failure_response("Invalid receiver_id. Please try again!")

#   start_time = datetime(start_time_year, start_time_month,
#                         start_time_day, start_time_hour, start_time_minute, 0)
#   end_time = datetime(end_time_year, end_time_month,
#                       end_time_day, end_time_hour, end_time_minute, 0)
#   # if sender_id = receiver_id: accepted = true

#   if name is None or start_time is None or end_time is None:
#     return failure_response("You are missing a field. Please try again!")

#   new_event = Event(name=name, start_time=start_time, end_time=end_time,
#                     sender_id=sender_id, receivers=receivers,
#                     message=message, accepted=False)
#   db.session.add(new_event)
#   db.session.commit()
#   return success_response(new_event.serialize(), 201)


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=8000, debug=True)
