from main import MainPage, PREAMBLE

class DatastoreProfile(MainPage):
	def get(self, num_bytes, num_properties):
		result = self.datastore_profiler.datastore_single(int(num_bytes), 
														  int(num_properties))
		self.response.write(PREAMBLE+
			'Datastore single put/get'
			'\nSuccess? {}\nPut time taken: {}\nGet time taken: {}\n'
			'Del time taken: {}'.
			format(result['correct'],
				   result['put_time'],
				   result['get_time'],
				   result['del_time']))

class DatastoreProfileOld(MainPage):
	def get(self, num_bytes):
		result = self.datastore_profiler.datastore_single_old(int(num_bytes))
		self.response.write(PREAMBLE+
			'Old datastore single put/get'
			'\nSuccess? {}\nPut time taken: {}\nGet time taken: {}\n'
			'Del time taken: {}'.
			format(result['correct'],
				   result['put_time'],
				   result['get_time'],
				   result['del_time']))

class DatastoreProfileOldMulti(MainPage):
	def get(self, num_bytes, num_entities):
		result = self.datastore_profiler.datastore_multi_old(int(num_bytes),
															 int(num_entities))
		self.response.write(PREAMBLE+
			'Old datastore batch put/get'
			'\nSuccess? {}\nPut time taken: {}\nGet time taken: {}\n'
			'Del time taken: {}'.
			format(result['correct'],
				   result['put_time'],
				   result['get_time'],
				   result['del_time']))

class DatastoreProfileMulti(MainPage):
	def get(self, num_bytes, num_properties, num_entities):
		result = self.datastore_profiler.datastore_multi(int(num_bytes), 
														 int(num_properties),
														 int(num_entities))
		self.response.write(PREAMBLE+
			'Datastore single put/get'
			'\nSuccess? {}\nPut time taken: {}\nGet time taken: {}\n'
			'Del time taken: {}'.
			format(result['correct'],
				   result['put_time'],
				   result['get_time'],
				   result['del_time']))