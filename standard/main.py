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

import webapp2
import profile_memcache
import profile_datastore

PREAMBLE = '\n'*20
API_ENDPOINTS = (PREAMBLE +
				 'Hello, everyone!\nThis is a web app we will use to test GAE Standard.\n'
				 'Endpoints:\n'
				 ' - /profile_memcache&bytes=(int)'
				 ' -- a single memcache get/set operation\n'
				 ' - /profile_memcache&bytes=(int)&threads=(int)'
				 ' -- multiple threads of memcache get operations on a single key\n'
				 ' - /profile_memcache&bytes=(int)&values=(int)'
				 ' -- a synchronous multiget/multiset memcache operation\n'
				 ' - /profile_memcache&bytes=(int)&gets=(int)&sleep=(bool)'
				 ' -- async multiget memcache operations on the same key\n'
				 ' - /profile_memcache_unique&bytes=(int)&gets=(int)&sleep=(bool)'
				 ' -- async multiget memcache operations on different keys\n'
				 ' - /profile_datastore&bytes=(int)&properties=(int)'
				 ' -- a single datastore put/get operation\n'
				 ' - /profile_datastore&bytes=(int)&properties=(int)&entities=(int)'
				 ' -- a datastore multiput/multiget operation\n'
				 ' - /profile_datastore_old&bytes=(int)'
				 ' -- a single old datastore put/get operation\n'
				 ' - /profile_datastore_old&bytes=(int)&entities=(int)'
				 ' -- a batch old datastore put/get operation\n')

class MainPage(webapp2.RequestHandler):
	def __init__(self, request, response):
		super(MainPage, self).__init__(request, response)
		self.memcache_profiler = profile_memcache.MemcacheProfiler()
		self.datastore_profiler = profile_datastore.DatastoreProfiler()
		self.response.headers['Content-Type'] = 'text/plain'

	def get(self):
		self.response.write(API_ENDPOINTS)

from endpoints_memcache import (MemcacheProfile, MemcacheProfileThreaded, 
								 MemcacheProfileMulti, MemcacheProfileRepeated, 
								 MemcacheProfileRepeatedUnique)
from endpoints_datastore import (DatastoreProfile, DatastoreProfileMulti,
								 DatastoreProfileOld, DatastoreProfileOldMulti)

app = webapp2.WSGIApplication([
    ('/', MainPage),
    (r'/profile_memcache&bytes=(\d+)', 
    	MemcacheProfile),
    (r'/profile_memcache&bytes=(\d+)&threads=(\d+)', 
    	MemcacheProfileThreaded),
    (r'/profile_memcache&bytes=(\d+)&values=(\d+)', 
    	MemcacheProfileMulti),
    (r'/profile_memcache&bytes=(\d+)&gets=(\d+)&sleep=(.*)', 
    	MemcacheProfileRepeated),
    (r'/profile_memcache_unique&bytes=(\d+)&gets=(\d+)&sleep=(.*)', 
    	MemcacheProfileRepeatedUnique),
    (r'/profile_datastore&bytes=(\d+)&properties=(\d+)', 
    	DatastoreProfile),
    (r'/profile_datastore&bytes=(\d+)&properties=(\d+)&entities=(\d+)', 
    	DatastoreProfileMulti),
    (r'/profile_datastore_old&bytes=(\d+)', 
    	DatastoreProfileOld),
    (r'/profile_datastore_old&bytes=(\d+)&entities=(\d+)',
    	DatastoreProfileOldMulti)

], debug=True)
