"""Some functions for making datastore requests."""
import base64
import os
import time

import google
reload(google)
import google.appengine.ext.db
import google.appengine.ext.ndb


import models


def single_datastore(num_bytes):
    """Make a single request to datastore db.

    - num_bytes: number of bytes to assign to data properties
    Return: the time for put, get, and delete operations,
            and whether the data access succeeded.
    """
    ds = google.cloud.datastore.Client()
    key = ds.key('Sample', 'sample_row')
    sample = google.cloud.datastore.Entity(key=key)
    sample.update({
        'name': base64.b64encode(os.urandom(num_bytes)),
        'email': base64.b64encode(os.urandom(num_bytes))
    })

    # time put
    put_start = time.time()
    ds.put(sample)
    put_end = time.time()

    # time get
    get_start = time.time()
    result = ds.get(key)
    get_end = time.time()

    # time delete
    delete_start = time.time()
    ds.delete(key)
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
    ds = google.cloud.datastore.Client()
    entities, keys = [], []
    for i in range(num_entities):
        keys.append(ds.key('Sample', 'row%s' % i))
        entities.append(google.cloud.datastore.Entity(key=keys[-1]))
        entities[-1].update({
            'name': base64.b64encode(os.urandom(num_bytes)),
            'email': base64.b64encode(os.urandom(num_bytes))
        })

    # time put
    put_start = time.time()
    ds.put_multi(entities)
    put_end = time.time()

    # time get
    get_start = time.time()
    result = ds.get_multi(keys)
    get_end = time.time()

    # time delete
    delete_start = time.time()
    ds.delete_multi(keys)
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
    # disable memcache
    google.appengine.ext.ndb.get_context().set_memcache_policy(False)
    google.appengine.ext.ndb.get_context().set_cache_policy(False)

    # create an entity
    sample = sample = models.SampleNdbModel(
        name=base64.b64encode(os.urandom(num_bytes)),
        email=base64.b64encode(os.urandom(num_bytes)))

    # time put
    put_start = time.time()
    key = sample.put()
    put_end = time.time()

    # time get
    get_start = time.time()
    result = key.get()
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
    # disable memcache
    google.appengine.ext.ndb.get_context().set_memcache_policy(False)
    google.appengine.ext.ndb.get_context().set_cache_policy(False)

    # create an array of entities
    entities = []
    for i in range(num_entities):
        entities.append(models.SampleNdbModel(
            name=base64.b64encode(os.urandom(num_bytes)),
            email=base64.b64encode(os.urandom(num_bytes))))

    # time put
    put_start = time.time()
    keys = google.appengine.ext.ndb.put_multi(entities)
    put_end = time.time()

    # time get
    get_start = time.time()
    result = google.appengine.ext.ndb.get_multi(keys, use_memcache=False)
    get_end = time.time()

    # time delete
    delete_start = time.time()
    google.appengine.ext.ndb.delete_multi(keys)
    delete_end = time.time()

    return {
        'put_time': put_end - put_start,
        'get_time': get_end - get_start,
        'del_time': delete_end - delete_start,
        'correct': result == entities
    }
