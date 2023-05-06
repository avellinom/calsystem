from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import base64
import boto3
import io
from io import BytesIO
from mimetypes import guess_extension, guess_type
import os
from PIL import Image
import random
import re
import string

db = SQLAlchemy()

# AWS constants
EXTENSIONS = ["png", "gif", "jpg", "jpeg"]
BASE_DIR = os.getcwd()
S3_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME")
S3_BASE_URL = f"https://{S3_BUCKET_NAME}.s3.us-east-1.amazonaws.com"

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


class Asset(db.Model):
  """
  Asset model for calendar image
  """
  __tablename__ = "assets"
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  base_url = db.Column(db.String, nullable=True)
  salt = db.Column(db.String, nullable=False)
  extension = db.Column(db.String, nullable=False)
  width = db.Column(db.Integer, nullable=False)
  height = db.Column(db.Integer, nullable=False)

  def __init__(self, **kwargs):
    """
    Initializes an asset object
    """
    self.create(kwargs.get("image_data"))

  def create(self, image_data):
    """
    For a base64 image:
      1. Rejects if it's bad filetype
      2. Generates a random string for the image filename
      3. Decode the image and attempt to upload to AWS
    """
    try:
      ext = guess_extension(guess_type(image_data)[0])[1:]

      # Only accept support file extensions
      if ext not in EXTENSIONS:
        raise Exception(f"Extension {ext} not supported")

      # Generate random string
      salt = "".join(
          random.SystemRandom().choice(
              string.ascii_uppercase + string.digits
          )
          for _ in range(16)
      )

      # Decode the image
      # a) remove base64 header
      img_str = re.sub("^data:image/.+;base64,", "", image_data)
      img_data = base64.b64decode(img_str)
      img = Image.open(BytesIO(img_data))

      self.base_url = S3_BASE_URL
      self.salt = salt
      self.extension = ext
      self.width = img.width
      self.height = img.height

      img_filename = f"{self.salt}.{self.extension}"
      self.upload(img, img_filename)
    except Exception as e:
      print(f"Error while creating image: {e}")

  def serialize(self):
    """
    Serializes an asset object
    """
    return {
        "url": f"{self.base_url}/{self.salt}.{self.extension}"
    }

  def upload(self, img, img_filename):
    """
    Upload image via AWS
    """
    try:
      # save img temporarily on server
      img_temploc = f"{BASE_DIR}/{img_filename}"
      img.save(img_temploc)

      # upload image to S3
      s3_client = boto3.client("s3")
      s3_client.upload_file(img_temploc, S3_BUCKET_NAME, img_filename)

      # make s3 accesspublic
      s3_resource = boto3.resource("s3")
      object_acl = s3_resource.ObjectAcl(S3_BUCKET_NAME, img_filename)
      object_acl.put(ACL="public-read")

      # remove image from server
      os.remove(img_temploc)

    except Exception as e:
      print(f"Error while uploading image: {e}")


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
      db.String, db.ForeignKey("user.email"), nullable=False)
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
    return {"id": self.id, "name": self.name, "color": self.color,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "sender_email": self.sender_email,
            "receiver_emails": [r.get_email() for r in self.receiver_emails]}


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
    return both_events

  def serialize(self):
    """
    Serializes a User object
    """
    return {"email": self.email, "events": [e.serialize() for e in self.get_both_events()]}

  def get_sent_events(self):
    """
    Get all the events the user has sent
    """
    return {"events": [e.serialize() for e in self.events_sent]}

  def get_email(self):
    """
    Simple serializes a user object
    """
    return self.email
