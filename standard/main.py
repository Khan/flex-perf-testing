# Copyright 2016 Google Inc.
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

from flask import Flask
from flask import request
from flask import jsonify
import logging

import profile_memcache
import profile_datastore

app = Flask(__name__)


PREAMBLE = '<br/>' * 20
API_ENDPOINTS = (PREAMBLE +
                 """Hello, everyone!
                 <br/>This is a web app we will use to test GAE Standard.<br/>
                 Endpoints:<br/>
                  - /profile_memcache?bytes=(int)
                  -- a single memcache get/set operation<br/>
                  - /profile_memcache?bytes=(int)&threads=(int)
                  -- multiple threads of memcache get operations
                     on a single key<br/>
                  - /profile_memcache?bytes=(int)&values=(int)
                  -- synchronous multiget/multiset memcache operation<br/>
                  - /profile_memcache?bytes=(int)&gets=(int)&sleep=(true/false)
                  -- async multiget memcache operations on the same key<br/>
                  - /profile_memcache_unique?bytes=(int)&gets=(int)&
                  sleep=(true/false)
                  -- async multiget memcache operations on different keys<br/>
                  <br/>
                  - /profile_ndb?bytes=(int)
                  -- a single ndb put/get operation<br/>
                  - /profile_ndb?bytes=(int)&entities=(int)
                  -- an ndb multiput/multiget operation<br/>
                  <br/>
                  - /profile_datastore?bytes=(int)
                  -- a single datastore put/get operation<br/>
                  - /profile_datastore?bytes=(int)&entities=(int)
                  -- a batch datastore put/get operation<br/>""")


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


@app.route('/profile_memcache')
def prof_memcache():
    num_bytes = int(request.args.get('bytes'))
    num_threads = request.args.get('threads')
    num_values = request.args.get('values')
    num_gets = request.args.get('gets')
    sleep = (request.args.get('sleep') == 'true')

    num_threads = int(num_threads) if num_threads else None
    num_values = int(num_values) if num_values else None
    num_gets = int(num_gets) if num_gets else None

    if not (num_threads or num_values or num_gets):
        return jsonify(profile_memcache.single(num_bytes))
    elif num_threads:
        return jsonify(profile_memcache.threaded(num_bytes, num_threads))
    elif num_values:
        return jsonify(profile_memcache.multi(num_bytes, num_values))
    else:
        return jsonify(profile_memcache.repeated(num_bytes, num_gets, sleep))


@app.route('/profile_memcache_unique')
def prof_memcache_unique():
    num_bytes = int(request.args.get('bytes'))
    num_gets = int(request.args.get('gets'))
    sleep = (request.args.get('sleep') == 'true')

    return jsonify(profile_memcache.repeated_unique(num_bytes,
                                                    num_gets,
                                                    sleep))


@app.route('/profile_datastore')
def prof_datastore():
    num_bytes = int(request.args.get('bytes'))
    num_entities = request.args.get('entities')

    num_entities = int(num_entities) if num_entities else None

    if not num_entities:
        return jsonify(profile_datastore.single_datastore(num_bytes))
    else:
        return jsonify(profile_datastore.multi_datastore(num_bytes,
                                                         num_entities))


@app.route('/profile_ndb')
def prof_ndb():
    num_bytes = int(request.args.get('bytes'))
    num_entities = request.args.get('entities')

    num_entities = int(num_entities) if num_entities else None

    if not num_entities:
        return jsonify(profile_datastore.single_ndb(num_bytes))
    else:
        return jsonify(profile_datastore.multi_ndb(num_bytes, num_entities))

if __name__ == '__main__':
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
# [END app]
