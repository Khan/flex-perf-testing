# TODO: Switch over to fixed model

from google.appengine.ext import db, ndb


class SampleNdbModel(ndb.Expando):
    # An empty model
    # Expando allows us to add properties to this model
    pass


class SampleModel(db.Model):
    # Sample model for testing
    name = db.StringProperty()
    email = db.StringProperty()

    def __eq__(self, other):
        # Check that name and email properties are equal
        return self.name == other.name and self.email == other.email
