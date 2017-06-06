# TODO: Switch over to fixed model

from google.appengine.ext import ndb
from google.appengine.ext import db

class SampleNdbModel(ndb.Expando):
    # An empty model
    # Expando allows us to add properties to this model
    pass
