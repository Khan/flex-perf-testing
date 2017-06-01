from main import MainPage, PREAMBLE

class MemcacheProfile(MainPage):
	def get(self, num_bytes):
		result = self.memcache_profiler.memcache_single(int(num_bytes))
		self.response.write(PREAMBLE+
			'Success? {}\nSet time taken: {}\n'
			'Get time taken: {}\nDel time taken: {}'.
			format(result['correct'], 
			       result['set_time'],
			       result['get_time'],
			       result['del_time']))

class MemcacheProfileThreaded(MainPage):
	def get(self, num_bytes, num_gets):
		result = self.memcache_profiler.memcache_threaded(int(num_bytes), 
												 int(num_gets))
		self.response.write(PREAMBLE+
			'Success? {}\nGet time taken: {}'.
			format(result['correct'],
				   result['get_time']))

class MemcacheProfileMulti(MainPage):
	def get(self, num_bytes, num_values):
		result = self.memcache_profiler.memcache_multi(int(num_bytes), 
											  int(num_values))
		self.response.write(PREAMBLE+
			'Memcache multiget\nSet time taken: {}\n'
			'Get time taken: {}\nDel time taken: {}'.
			format(result['correct'],
				   result['set_time'],
				   result['get_time'],
				   result['del_time']))

class MemcacheProfileRepeated(MainPage):
	def get(self, num_bytes, num_gets, sleep):
		result = self.memcache_profiler.memcache_repeated(int(num_bytes), 
												 int(num_gets), 
												 sleep=="true")
		self.response.write(PREAMBLE+
			'Memcache async multiget for same key'
			'\nSuccess? {}\nGet time taken: {}'.
			format(result['correct'],
				   result['get_time']))

class MemcacheProfileRepeatedUnique(MainPage):
	def get(self, num_bytes, num_gets, sleep):
		result = self.memcache_profiler.memcache_repeated_unique(int(num_bytes), 
														int(num_gets), 
														sleep=="true")
		self.response.write(PREAMBLE+
			'Memcache async multiget/multiset for different keys'
			'\nSuccess? {}\nSet time taken: {}\nGet time taken: {}'.
			format(result['correct'],
				   result['set_time'],
				   result['get_time']))