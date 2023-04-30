from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

#  association tables here
association_table_sender = db.Table(
  "sender_association",
  db.Column("event_id", db.Integer, db.ForeignKey("event.id")),
  db.Column("sender_id", db.Integer, db.ForeignKey("user.id"))
)

association_table_receiver = db.Table(
  "receiver_association",
  db.Column("event_id", db.Integer, db.ForeignKey("event.id")),
  db.Column("receiver_id", db.Integer, db.ForeignKey("user.id"))
)


# classes for tables here
class Event(db.Model):
  """
  Event model
  """
  __tablename__ = "event"
  id = db.Column(db.Integer, primary_key = True, autoincrement=True) #do we need this?
  name = db.Column(db.String, nullable = False) #title of event
  start_time = db.Column(db.Time, nullable=False) 
  end_time = db.Column(db.Time, nullable=False)
  sender_id = db.relationship("User", secondary = association_table_sender, back_populates = "events_accepted")
  receiver_id = db.relationship("User", secondary = association_table_receiver, back_populates = "events_pending")
  message = db.Column(db.String, nullable = True) #description of event, can be left empty
  accepted = db.Column(db.Bool, nullable = False)

  def __init__(self, **kwargs):
    """
    Initializes an event object
    """
    self.name = kwargs.get("name", "Event Request")
    self.start_time = kwargs.get("start_time") #What would be the best way for the client to put in times? if start and end time are left empty returns an error
    self.end_time = kwargs.get("end_time")
    self.sender_id = kwargs.get("sender_id") #should also return error if no receiver_id specified
    self.receiver_id = kwargs.get("receiver_id") #should also return error if no receiver_id specified
    self.message = kwargs.get("message") 
    self.accepted = kwargs.get("accepted")
  

class User(db.Model):
  """
  User Model
  """
  id = db.Column(db.Integer, primary_key = True, autoincrement=True)
  username = db.Column(db.String, nullable = False) #the usernames won't be unique, but we will just go based off of ids
  password = db.Column(db.String, nullable = False)
  events_accepted = db.relationship("Event", secondary = association_table_sender, back_populates = "sender_id", cascade ="delete") #if user gets deleted, then events accepted and pending should get deleted too
  events_pending = db.relationship("Event", secondary = association_table_receiver, back_populates = "receiver_id", cascade = "delete")

  def __init__(self, **kwargs):
    """
    Initializes a user object
    """
    self.username = kwargs.get("username", "")
    self.password = kwargs.get("password", "")

  def get_events_accepted(self):
    """
    Returns all events that have been accepted associated with this user
    """
    pass

  def get_events_pending(self):
    """
    Returns all events that are pending associated with this user
    """
    pass

  





#Questions: 
#Do we want the user to give a day and then we tell them the events of that day?
#What would be the best way so that only the person with that username can accept that event request?
#How can we organize all the events?
#Do we still need the serialize functions if we are going to be using DockerHub, Google Cloud?

#Considerations:
#do not want the times to conflict for events

#Possible Additions:
#-Adding different calendars for a user (personal, work, etc)
#Calendar Table
#can have different calendars for a user

# class Calendar(db.Model):
#   """
#   Calendar model
#   """
#   __tablename__ = "calendar"
#   id = db.Column(db.Integer, primary_key = True, autoincrement = True)
#   name = db.Column(db.String, nullable = False)
#   events = db.Relationship()

