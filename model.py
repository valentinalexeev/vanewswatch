#!env python
from google.appengine.ext import db

class NewsWatchFilter(db.Model):
    owner = db.UserProperty()
    filterCriteria = db.StringProperty()
    actionList = db.StringListProperty()
    