# Copyright 2015 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START app]
import logging

from flask import Flask

import profile_datastore
import profile_memcache

app = Flask(__name__)

PREAMBLE = '<br/>' * 12
API_ENDPOINTS = (PREAMBLE +
                 """Hello, everyone!
                 <br/>This is a web app we will use to test GAE Flex.<br/>
                 Endpoints:<br/>
                  - /profile_memcache&bytes=(int)
                  -- a single memcache get/set operation<br/>
                  - /profile_memcache&bytes=(int)&threads=(int)
                  -- multiple threads of memcache get operations
                     on a single key<br/>
                  - /profile_memcache&bytes=(int)&values=(int)
                  -- synchronous multiget/multiset memcache operation<br/>
                  - /profile_memcache&bytes=(int)&gets=(int)&sleep=(0/1)
                  -- async multiget memcache operations on the same key<br/>
                  - /profile_memcache_unique&bytes=(int)&gets=(int)&sleep=(0/1)
                  -- async multiget memcache operations on different keys<br/>
                  <br/>
                  - /profile_datastore&bytes=(int)
                  -- a single datastore put/get operation<br/>
                  - /profile_datastore&bytes=(int)&entities=(int)
                  -- a datastore multiput/multiget operation<br/>
                  <br/>
                  - /profile_datastore_old&bytes=(int)
                  -- a single old datastore put/get operation<br/>
                  - /profile_datastore_old&bytes=(int)&entities=(int)
                  -- a batch old datastore put/get operation<br/>""")


@app.route('/')
def hello():
    """Return a friendly HTTP greeting."""
    return API_ENDPOINTS


@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500


@app.route('/profile_memcache&bytes=<int:num_bytes>',
           defaults={'num_threads': None, 'num_values': None})
@app.route('/profile_memcache&bytes=<int:num_bytes>'
           '&threads=<int:num_threads>',
           defaults={'num_values': None})
@app.route('/profile_memcache&bytes=<int:num_bytes>'
           '&values=<int:num_values>',
           defaults={'num_threads': None})
def prof_memcache(num_bytes, num_threads, num_values):
    if not num_threads and not num_values:
        result = profile_memcache.single(num_bytes)
        return (PREAMBLE +
                'Memcache single: Correct? {}<br/>'
                'Set time: {}<br/>Get time: {}<br/>Del time: {}'.format(
                    result['correct'], result['set_time'],
                    result['get_time'], result['del_time']))
    elif num_threads:
        result = profile_memcache.threaded(num_bytes, num_threads)
        return (PREAMBLE +
                'Memcache threaded: Correct? {}<br/>'
                'Get time: {}'.format(
                    result['correct'], result['get_time']))
    else:
        result = profile_memcache.multi(num_bytes, num_values)
        return (PREAMBLE +
                'Memcache multi: Correct? {}<br/>'
                'Set time: {}<br/>Get time: {}<br/>Del time: {}'.format(
                    result['correct'], result['set_time'],
                    result['get_time'], result['del_time']))


@app.route('/profile_datastore_old&bytes=<int:num_bytes>',
           defaults={'num_entities': None})
@app.route('/profile_datastore_old&bytes=<int:num_bytes>'
           '&entities=<int:num_entities>')
def prof_datastore_old(num_bytes, num_entities):
    if not num_entities:
        result = profile_datastore.single_old(num_bytes)
    else:
        result = profile_datastore.multi_old(num_bytes, num_entities)
    return (PREAMBLE +
            'Datastore old: Correct? {}<br/>'
            'Put time: {}<br/>Get time: {}<br/>Del time: {}'.format(
                result['correct'], result['put_time'],
                result['get_time'], result['del_time']))


@app.route('/profile_datastore&bytes=<int:num_bytes>',
           defaults={'num_entities': None})
@app.route('/profile_datastore&bytes=<int:num_bytes>'
           '&entities=<int:num_entities>')
def prof_datastore(num_bytes, num_entities):
    if not num_entities:
        result = profile_datastore.single(num_bytes)
    else:
        result = profile_datastore.multi(num_bytes,
                                         num_entities)
    return(PREAMBLE +
           'Datastore ndb: Correct? {}<br/>'
           'Put time: {}<br/>Get time: {}<br/>Del time: {}'.
           format(result['correct'], result['put_time'],
                  result['get_time'], result['del_time']))

if __name__ == '__main__':
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
# [END app]
