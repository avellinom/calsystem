from flask_sqlalchemy import SQLAlchemy
from datetime import datetime 

db = SQLAlchemy()

"""
Overview of Data Structuring:
* Sender <-> Event is one-to-many
* Receiver <-> Event is many-to-many
"""

# association tables here
association_table_receiver = db.Table(
    "receiver_association",
    db.Column("event_id", db.Integer, db.ForeignKey("event.id")),
    db.Column("receivers", db.Integer, db.ForeignKey("user.id"))
)


# classes for tables here
class Event(db.Model):
  """
  Event model
  """
  __tablename__ = "event"
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  name = db.Column(db.String, nullable=False)  # title of event
  start_time = db.Column(db.DateTime, nullable=False)
  end_time = db.Column(db.DateTime, nullable=False)
  sender_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
  receivers = db.relationship(
      "User", secondary=association_table_receiver, back_populates="events_pending")
  message = db.Column(db.String, nullable=True)
  accepted = db.Column(db.Boolean, nullable=False)

  def __init__(self, **kwargs):
    """
    Initializes an event object
    """
    self.name = kwargs.get("name", "Event Request")
    # What would be the best way for the client to put in times? if start and end time are left empty returns an error
    self.start_time = kwargs.get("start_time")
    self.end_time = kwargs.get("end_time")
    # should also return error if no receiver_id specified
    self.sender_id = kwargs.get("sender_id")
    # should also return error if no receiver_id specified
    self.receivers = kwargs.get("receivers", "")
    self.message = kwargs.get("message")
    self.accepted = kwargs.get("accepted")

  def serialize(self):
    """
    Serializes an Event object
    """
    return {"id": self.id, "name": self.name, "start_time": self.start_time, 
            "end_time": self.end_time, "sender_id": self.sender_id, 
            "receivers": [r.simple_serialize() for r in self.receivers], "message": self.message, 
            "accepted": self.accepted }


class User(db.Model):
  """
  User Model
  """
  __tablename__ = "user"
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  # the usernames won't be unique, but we will just go based off of ids
  username = db.Column(db.String, nullable=False)
  password = db.Column(db.String, nullable=False)
  # if user gets deleted, then events accepted and pending should get deleted too
  events_accepted = db.relationship("Event", cascade="delete")
  events_pending = db.relationship(
      "Event", secondary=association_table_receiver, back_populates="receivers", cascade="delete")

  def __init__(self, **kwargs):
    """
    Initializes a user object
    """
    self.username = kwargs.get("username", "")
    self.password = kwargs.get("password", "")

  def serialize(self):
    """
    Serializes a User object
    """
    return {"id": self.id, "username": self.username, "password": self.password, "events_accepted":[e.serialize() for e in self.events_accepted], "events_pending":[e.serialize() for e in self.events_pending]}
  #Should we be serializing the password?

  def simple_serialize(self):
    """
    Simple serializes a user object
    """
    return {"id": self.id, "username": self.username}
 


# Questions:
# Do we want the user to give a day and then we tell them the events of that day?
# What would be the best way so that only the person with that username can accept that event request?
# How can we organize all the events?
# Do we still need the serialize functions if we are going to be using DockerHub, Google Cloud?

# Considerations:
# do not want the times to conflict for events

# Possible Additions:
# -Adding different calendars for a user (personal, work, etc)
# Calendar Table
# can have different calendars for a user


# class Calendar(db.Model):
#   """
#   Calendar model
#   """
#   __tablename__ = "calendar"
#   id = db.Column(db.Integer, primary_key = True, autoincrement = True)
#   name = db.Column(db.String, nullable = False)
#   events = db.Relationship()
