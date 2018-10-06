from google.appengine.ext import ndb
from datetime import datetime, timedelta

class User(ndb.Model):
    id = ndb.StringProperty(required=True)
    first_name = ndb.StringProperty(required=True)
    last_name = ndb.StringProperty(required=True)
    is_doctor = ndb.BooleanProperty(required=True)
    list = ndb.StringProperty(repeated=True)
    exit_date = ndb.DateProperty(required=False)
