from google.appengine.ext import db
from google.appengine.ext import ndb


class SampleNdbModel(ndb.Model):
    # Sample model for testing
    name = ndb.StringProperty()
    email = ndb.StringProperty()

    def __eq__(self, other):
        # Check that name and email properties are equal
        return self.name == other.name and self.email == other.email


class SampleModel(db.Model):
    # Sample model for testing
    name = db.StringProperty()
    email = db.StringProperty()

    def __eq__(self, other):
        # Check that name and email properties are equal
        return self.name == other.name and self.email == other.email
