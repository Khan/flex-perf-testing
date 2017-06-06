import Queue
import base64
import logging
import os
import threading
import time

from google.appengine.api import apiproxy_stub_map
from google.appengine.api import memcache


def _wait_any_fast(rpcs, sleep, deadline=1):
    # if ka_globals.is_dev_server:
    if True:
        # Our RPCs on dev aren't truly asynchronous, so we won't bother doing
        # anything fancy
        while True:
            finished = apiproxy_stub_map.UserRPC.wait_any(rpcs)
            if finished is not None:
                return finished

    stop = time.time() + deadline
    while time.time() < stop:
        finished, r = apiproxy_stub_map.UserRPC._UserRPC__check_one(rpcs)
        if finished is not None:
            return finished
        if sleep:
            time.sleep(0.0001)
    raise Exception('RPC deadline exceeded')


class MemcacheProfiler:
    # Some convenience methods for Memcache profiling.

    def memcache_single(self, num_bytes):
        """
        Make a single request to memcache.

        - num_bytes: number of bytes to attach to the key
        Return: the time for get, set, and delete operations,
                and whether the data access succeeded.
        """
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

    def memcache_threaded(self, num_bytes, num_gets):
        """
        Make multiple threads of get requests from memcache.

        - num_bytes: number of bytes to attach to the key
        - num_gets: number of gets to call (each in own thread)
        Return: the time for the get operations,
                and whether the data access succeeded.
        """
        # create and set the (key, data) pair
        data = os.urandom(num_bytes)
        key = 'profile_memcache_%s' % base64.b64encode(os.urandom(16))
        logging.debug("Profiling memcache for key %s" % key)
        success = memcache.set(key, data)
        if not success:
            raise RuntimeError("Memcache set failed!")

        # create the queue
        queue = Queue.Queue()

        # define the function to run
        def getter():
            queue.put(memcache.get(key))

        # time the get operations
        get_start = time.time()
        # call getter() in multiple threads
        for _ in xrange(num_gets):
            threading.Thread(target=getter).start()
        # extract the result from the queue
        data_again = queue.get()
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

    def memcache_multi(self, num_bytes, num_vals):
        """
        Make a batch set and get request to memcache.

        - num_bytes: number of bytes to attach to the key
        - num_vals: number of (key, value) pairs in batch
        Return: the time for the set, get, and delete operations,
                and whether the data access succeeded.
        """
        # create the data and set to memcache
        data = {
            'profile_memcache_%s' % base64.b64encode(os.urandom(16)):
            os.urandom(num_bytes)
            for _ in xrange(num_vals)}
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

    def memcache_repeated(self, num_bytes, num_gets, sleep):
        """
        Make multiple async get requests to the same key in memcache.

        - num_bytes: number of bytes to attach to the key
        - num_gets: number of async get requests to make
        - sleep: ? TODO(kasrakoushan): figure out
        Return: the time for the get operation, and
                whether the data access succeeded.
        """
        # create and set the data
        data = os.urandom(num_bytes)
        key = 'profile_memcache_%s' % base64.b64encode(os.urandom(16))
        logging.debug("Profiling memcache for key %s" % key)
        success = memcache.set(key, data)
        if not success:
            raise RuntimeError("Memcache set failed!")

        client = memcache.Client()

        # time get
        get_start = time.time()
        rpcs = [client.get_multi_async([key]) for _ in xrange(num_gets)]
        data_again = _wait_any_fast(rpcs, sleep).get_result().get(key)
        get_end = time.time()

        # check correctness of get
        if data != data_again:
            logging.debug("data: %s" % data[:1000])
            if isinstance(data_again, basestring):
                logging.debug("data_again: %s" % data_again[:1000])
            else:
                logging.debug("data_again not a string: %s" % data_again)

        # delete data
        success = memcache.delete(key)
        if not success:
            raise RuntimeError("Memcache delete failed!")

        return {
            'get_time': get_end - get_start,
            'correct': data == data_again,
        }

    def memcache_repeated_unique(self, num_bytes, num_gets, sleep):
        """
        Make multiple async get requests to different keys in memcache.

        - num_bytes: number of bytes to attach to each key
        - num_gets: number of keys to set
        - sleep: ? TODO(kasrakoushan): figure out
        Return: the time for the get operation, and
                whether the data access succeeded.
        """
        # create and set the data
        data = os.urandom(num_bytes)
        keys = ['profile_memcache_%s' % base64.b64encode(os.urandom(16))
                for _ in xrange(num_gets)]
        failures = memcache.set_multi({key: data for key in keys})
        if failures:
            logging.debug("Failures: %s" % failures)
            raise RuntimeError("Memcache set failed!")

        # time get
        client = memcache.Client()
        get_start = time.time()
        gets = [client.get_multi_async([key]) for key in keys]
        result = _wait_any_fast(gets, sleep).get_result()
        data_again = result[result.keys()[0]]
        get_end = time.time()

        # check correctness of get
        if data != data_again:
            logging.debug("data: %s" % data[:1000])
            if isinstance(data_again, basestring):
                logging.debug("data_again: %s" % data_again[:1000])
            else:
                logging.debug("data_again not a string: %s" % data_again)

        # delete data
        success = memcache.delete_multi(keys)
        if not success:
            raise RuntimeError("Memcache delete failed!")

        return {
            'get_time': get_end - get_start,
            'correct': data == data_again,
        }
