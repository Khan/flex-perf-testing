import logging
import os
import base64
import time
import queue
import threading

import pylibmc

# [START client]
# Environment variables are defined in app.yaml.
if os.environ.get('USE_GAE_MEMCACHE'):
    MEMCACHE_SERVER = ':'.join([
        os.environ.get('GAE_MEMCACHE_HOST', 'localhost'), 
        os.environ.get('GAE_MEMCACHE_PORT', '11211')])
else:
    MEMCACHE_SERVER = os.environ.get('MEMCACHE_SERVER', 'localhost:11211')

MEMCACHE_USERNAME = os.environ.get('MEMCACHE_USERNAME')
MEMCACHE_PASSWORD = os.environ.get('MEMCACHE_PASSWORD')

memcache_client = pylibmc.Client(
    [MEMCACHE_SERVER], binary=True,
    username=MEMCACHE_USERNAME, password=MEMCACHE_PASSWORD)
memcache = memcache_client
# [END client]

class MemcacheProfiler:
    # Some convenience methods for Memcache profiling.

    '''
    Make a single request to memcache.
    - num_bytes: number of bytes to attach to the key

    Return: the time for get, set, and delete operations,
            and whether the data access succeeded.
    '''
    def memcache_single(self, num_bytes):
        # create the data and key
        data = os.urandom(num_bytes)
        key = 'profile_memcache_%s' % base64.b64encode(os.urandom(16))
        logging.debug("Profiling memcache for key %s" % key)

        # time set
        set_start = time.time()
        success = memcache.set(key, data)
        set_end = time.time()
        if not success:
            raise RuntimeError("Memcache set failed!")

        # time get
        get_start = time.time()
        data_again = memcache.get(key)
        get_end = time.time()

        if data != data_again:
            logging.debug("data: %s" % data[:1000])
            if isinstance(data_again, basestring):
                logging.debug("data_again: %s" % data_again[:1000])
            else:
                logging.debug("data_again not a string: %s" % data_again)

        # Time delete
        delete_start = time.time()
        memcache.delete(key)
        delete_end = time.time()

        return {
            'get_time': get_end - get_start,
            'set_time': set_end - set_start,
            'del_time': delete_end - delete_start,
            'correct': data == data_again,
        }

    '''
    Make multiple threads of get requests from memcache.
    - num_bytes: number of bytes to attach to the key
    - num_gets: number of gets to call (each in own thread)

    Return: the time for the get operations,
            and whether the data access succeeded.
    '''
    def memcache_threaded(self, num_bytes, num_gets):
        # create and set the (key, data) pair
        data = os.urandom(num_bytes)
        key = 'profile_memcache_%s' % base64.b64encode(os.urandom(16))
        logging.debug("Profiling memcache for key %s" % key)
        success = memcache.set(key, data)
        if not success:
            raise RuntimeError("Memcache set failed!")

        # create the queue
        q = queue.Queue()

        # define the function to run
        def getter():
            q.put(memcache.get(key))

        # time the get operations
        get_start = time.time()
        # call getter() in multiple threads
        for _ in range(num_gets):
            threading.Thread(target=getter).start()
        # extract the result from the queue
        data_again = q.get()
        get_end = time.time()

        if data != data_again:
            logging.debug("data: %s" % data[:1000])
            if isinstance(data_again, basestring):
                logging.debug("data_again: %s" % data_again[:1000])
            else:
                logging.debug("data_again not a string: %s" % data_again)

        # delete the key
        memcache.delete(key)
        return {
            'get_time': get_end - get_start,
            'correct': data == data_again,
        }

    '''
    Make a batch set and get request to memcache.
    - num_bytes: number of bytes to attach to the key
    - num_vals: number of (key, value) pairs in batch

    Return: the time for the set, get, and delete operations,
            and whether the data access succeeded.
    '''
    def memcache_multi(self, num_bytes, num_vals):
        # create the data and set to memcache
        data = {
            'profile_memcache_%s' % base64.b64encode(os.urandom(16)):
            os.urandom(num_bytes)
            for _ in range(num_vals)}
        # time set
        set_start = time.time()
        failures = memcache.set_multi(data)
        set_end = time.time()
        if failures:
            logging.debug("Failures: %s" % failures)
            raise RuntimeError("Memcache set failed!")

        # time get
        get_start = time.time()
        data_again = memcache.get_multi(data.keys())
        get_end = time.time()

        # time delete
        delete_start = time.time()
        success = memcache.delete_multi(data.keys())
        delete_end = time.time()
        if not success:
            raise RuntimeError("Memcache delete failed!")

        return {
            'get_time': get_end - get_start,
            'set_time': set_end - set_start,
            'del_time': delete_end - delete_start,
            'correct': data == data_again,
        }
