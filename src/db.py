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
    db.Column("receiver_emails", db.Integer, db.ForeignKey("user.email"))
)

# classes for tables here


class Event(db.Model):
  """
  Event model
  """
  __tablename__ = "event"
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  name = db.Column(db.String, nullable=False)  # title of event
  color = db.Column(db.String, nullable=False)
  start_time = db.Column(db.DateTime, nullable=False)
  end_time = db.Column(db.DateTime, nullable=False)
  sender_email = db.Column(
      db.Integer, db.ForeignKey("user.email"), nullable=False)
  receiver_emails = db.relationship(
      "User", secondary=association_table_receiver, back_populates="events_received")

  def __init__(self, **kwargs):
    """
    Initializes an event object
    """
    self.name = kwargs.get("name", "Event")
    self.color = kwargs.get("color", "Blue")
    # What would be the best way for the client to put in times? if start and end time are left empty returns an error
    self.start_time = kwargs.get("start_time")
    self.end_time = kwargs.get("end_time")
    # should also return error if no receiver_id specified
    self.sender_email = kwargs.get("sender_email")

  def serialize(self):
    """
    Serializes an Event object
    """
    return {"id": self.id, "name": self.name,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "sender_email": self.sender_email,
            "receiver_emails": [r.simple_serialize() for r in self.receiver_emails]}


class User(db.Model):
  """
  User Model
  """
  __tablename__ = "user"
  email = db.Column(db.String, nullable=False, primary_key=True)
  # if user gets deleted, then events accepted and pending should get deleted too
  events_sent = db.relationship("Event", cascade="delete")
  events_received = db.relationship(
      "Event", secondary=association_table_receiver, back_populates="receiver_emails", cascade="delete")

  def __init__(self, **kwargs):
    """
    Initializes a user object
    """
    self.email = kwargs.get("email")

  def get_both_events(self):
    """
    Returns all the events associated with this User
    """
    both_events = []
    for c in self.events_sent:
      both_events.append(c)
    for i in self.events_received:
      both_events.append(i)
    return (both_events)

  def serialize(self):
    """
    Serializes a User object
    """
    return {"email": self.email, "events": [e.serialize() for e in self.get_both_events()]}

  def simple_serialize(self):
    """
    Simple serializes a user object
    """
    return {"email": self.email}


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
