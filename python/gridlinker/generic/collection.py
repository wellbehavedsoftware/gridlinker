from __future__ import absolute_import
from __future__ import unicode_literals

from collections import OrderedDict

from wbs import freeze
from wbs import yamlx

class GenericCollection:

	def __init__ (self, context, type, path, schema):

		self.context = context
		self.type = type
		self.path = path
		self.schema = schema

		self.client = context.client

		self.cache = None

	def get_slow (self, record_name):

		record_key = "%s/%s" % (
			self.path,
			record_name)

		record_data = self.client.get_yaml (
			"%s/data" % record_key)

		return record_data

	def get_quick (self, record_name):

		self.auto_update_cache ()

		return self.data_cache [record_name]

	def exists_file_slow (self, record_name, file_name):

		record_key = "%s/%s" % (
			self.path,
			record_name)

		return self.client.exists (
			key = "%s/%s" % (record_key, file_name))

	def exists_file_quick (self, record_name, file_name):

		self.auto_update_cache ()

		key = "%s/%s/%s" % (
			self.path,
			record_name,
			file_name)

		return key in self.cache

	def auto_update_cache (self):

		if self.cache:
			return

		self.update_cache ()

	def update_cache (self):

		if not self.client.exists (self.path):

			self.cache = freeze ({})
			self.data_cache = freeze ({})
			self.all_list_cache = freeze ([])

			return

		cache = dict (self.client.get_tree (self.path))

		data_cache = OrderedDict ()
		all_list_cache = []

		for key, string_value in sorted (cache.items ()):

			if not key.endswith ("/data"):
				continue

			name = key [ 1 : len (key) - 5 ]

			value = yamlx.parse (string_value)

			data_cache [name] = value
			all_list_cache.append (( name, value ))

		self.cache = freeze (cache)
		self.data_cache = freeze (data_cache)
		self.all_list_cache = freeze (all_list_cache)

	def get_file_slow (self, record_name, file_name):

		record_key = "%s/%s" % (
			self.path,
			record_name)

		return self.client.get_raw (
			key = "%s/%s" % (record_key, file_name))

	def set (self, record_name, record_data):

		record_key = "%s/%s" % (
			self.path,
			record_name)

		self.client.set_yaml (
			key = "%s/data" % record_key,
			value = record_data,
			schema = self.schema)

	def set_file (self, record_name, file_name, file_contents):

		record_key = "%s/%s" % (
			self.path,
			record_name)

		self.client.set_raw (
			key = "%s/%s" % (record_key, file_name),
			value = file_contents)

	def get_all_values_slow (self):

		if not self.client.exists (self.path):
			return []

		ret = []

		for record_key, record_yaml \
		in self.client.get_tree (self.path):

			if not record_key.endswith ("/data"):
				continue

			record_data = yamlx.parse (record_yaml)

			ret.append (record_data)

		return ret

	def get_all_list_slow (self):

		if not self.client.exists (self.path):
			return []

		ret = []

		for record_key, record_yaml \
		in self.client.get_tree (self.path):

			if not record_key.endswith ("/data"):
				continue

			record_name = record_key [1:-5]

			try:

				record_data = yamlx.parse (record_yaml)

			except:

				raise Exception (
					"Error parsing %s" % record_key)

			ret.append ((record_name, record_data))

		return ret

	def get_all_list_quick (self):

		self.auto_update_cache ()

		return self.all_list_cache

	def get_all_dictionary_slow (self):

		if not self.client.exists (self.path):
			return {}

		ret = {}

		for record_key, record_yaml \
		in self.client.get_tree (self.path):

			if not record_key.endswith ("/data"):
				continue

			record_name = record_key [1:-5]

			try:

				record_data = yamlx.parse (record_yaml)

			except:

				raise Exception (
					"Error parsing %s" % record_key)

			ret [record_name] = record_data

		return ret

	def to_yaml (self, record_data):

		return yamlx.encode (
			self.schema,
			record_data)

	def exists_slow (self, record_name):

		record_key = "%s/%s" % (
			self.path,
			record_name)

		return self.client.exists (
			record_key)

# ex: noet ts=4 filetype=yaml
