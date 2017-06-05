import logging
import os
import base64
import time
import threading
from google.cloud import datastore

class DatastoreProfiler:
	'''
	Make a single request to datastore db.
	- num_bytes: number of bytes to assign to data properties

	Return: the time for put, get, and delete operations,
			and whether the data access succeeded.
	'''
	def datastore_single_old(self, num_bytes):
		ds = datastore.Client()
		key = ds.key('Sample', 'sample_row')
		sample = datastore.Entity(key=key)
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

	'''
	Make a batch request to datastore db.
	- num_bytes: number of bytes to assign to data properties
	- num_entities: number of entities to send in batch request

	Return: the time for put, get, and delete operations,
			and whether the data access succeeded.
	'''
	def datastore_multi_old(self, num_bytes, num_entities):
		# create an array of entities from SampleModel
		ds = datastore.Client()
		entities, keys = [], []
		for i in range(num_entities):
			keys.append(ds.key('Sample', 'row%s'%i))
			entities.append(datastore.Entity(key=keys[-1]))
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

	'''
	Make a single request to datastore ndb.
	- num_bytes: number of bytes to assign to data properties
	- num_properties: number of properties to attach to the entity

	Return: the time for put, get, and delete operations,
			and whether the data access succeeded.
	'''
	def datastore_single(self, num_bytes, num_properties):
		# create an entity with given number of properties
		sample = SampleNdbModel()
		for i in range(num_properties):
			# set each property to a random string
			num = base64.b64encode(os.urandom(num_bytes))
			exec('sample.property%s = num'%i)

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

	'''
	Make a batch request to datastore ndb.
	- num_bytes: number of bytes to assign to data properties
	- num_properties: number of properties to attach to the entity
	- num_entities: number of data entities (or rows) to set

	Return: the time for put, get, and delete operations,
			and whether the data access succeeded.
	'''
	def datastore_multi(self, num_bytes, num_properties, num_entities):
		# create an array of entities with given number of properties
		entities = []
		for i in range(num_entities):
			entities.append(SampleNdbModel())
			for j in range(num_properties):
				num = base64.b64encode(os.urandom(num_bytes))
				exec('entities[-1].property%s = num'%(j))

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
