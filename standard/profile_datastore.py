"""Some convenience methods for testing the datastore."""

import base64
import os
import time

from google.appengine.ext import db
from google.appengine.ext import ndb

import models


def single_datastore(num_bytes):
    """Make a single request to datastore db.

    - num_bytes: number of bytes to assign to data properties
    Return: the time for put, get, and delete operations,
            and whether the data access succeeded.
    """
    sample = models.SampleModel(name=base64.b64encode(os.urandom(num_bytes)),
                                email=base64.b64encode(os.urandom(num_bytes)))

    # time put
    put_start = time.time()
    db.put(sample)
    put_end = time.time()

    # get the key
    key = sample.key()

    # time get
    get_start = time.time()
    result = db.get(key)
    get_end = time.time()

    # time delete
    delete_start = time.time()
    db.delete(key)
    delete_end = time.time()

    return {
        'put_time': put_end - put_start,
        'get_time': get_end - get_start,
        'del_time': delete_end - delete_start,
        'correct': result == sample,
    }


def multi_datastore(num_bytes, num_entities):
    """Make a batch request to datastore db.

    - num_bytes: number of bytes to assign to data properties
    - num_entities: number of entities to send in batch request
    Return: the time for put, get, and delete operations,
            and whether the data access succeeded.
    """
    entities = []
    for i in range(num_entities):
        entities.append(models.SampleModel(
                        name=base64.b64encode(os.urandom(num_bytes)),
                        email=base64.b64encode(os.urandom(num_bytes))))

    # time put
    put_start = time.time()
    db.put(entities)
    put_end = time.time()

    # get the keys
    keys = [e.key() for e in entities]

    # time get
    get_start = time.time()
    result = db.get(keys)
    get_end = time.time()

    # time delete
    delete_start = time.time()
    db.delete(keys)
    delete_end = time.time()

    return {
        'put_time': put_end - put_start,
        'get_time': get_end - get_start,
        'del_time': delete_end - delete_start,
        'correct': result == entities,
    }


def single_ndb(num_bytes):
    """Make a single request to datastore ndb.

    - num_bytes: number of bytes to assign to data properties
    Return: the time for put, get, and delete operations,
            and whether the data access succeeded.
    """
    sample = models.SampleNdbModel(
        name=base64.b64encode(os.urandom(num_bytes)),
        email=base64.b64encode(os.urandom(num_bytes)))

    # time put
    put_start = time.time()
    key = sample.put()
    put_end = time.time()

    # time get
    get_start = time.time()
    result = key.get(use_memcache=False)
    get_end = time.time()

    # time delete
    delete_start = time.time()
    key.delete()
    delete_end = time.time()

    return {
        'put_time': put_end - put_start,
        'get_time': get_end - get_start,
        'del_time': delete_end - delete_start,
        'correct': result == sample,
    }


def multi_ndb(num_bytes, num_entities):
    """Make a batch request to datastore ndb.

    - num_bytes: number of bytes to assign to data properties
    - num_entities: number of data entities (or rows) to set
    Return: the time for put, get, and delete operations,
            and whether the data access succeeded.
    """
    # create an array of entities
    entities = []
    for i in range(num_entities):
        entities.append(models.SampleNdbModel(
            name=base64.b64encode(os.urandom(num_bytes)),
            email=base64.b64encode(os.urandom(num_bytes))))

    # time put
    put_start = time.time()
    keys = ndb.put_multi(entities)
    put_end = time.time()

    # time get
    get_start = time.time()
    result = ndb.get_multi(keys, use_memcache=False)
    get_end = time.time()

    # time delete
    delete_start = time.time()
    ndb.delete_multi(keys)
    delete_end = time.time()

    return {
        'put_time': put_end - put_start,
        'get_time': get_end - get_start,
        'del_time': delete_end - delete_start,
        'correct': result == entities
    }
