from __future__ import absolute_import
from __future__ import unicode_literals

from wbs import yamlx

class GenericCollection:

	def __init__ (self, context, type, path, schema):

		self.context = context
		self.type = type
		self.path = path
		self.schema = schema

		self.client = context.client

	def get (self, record_name):

		record_key = "%s/%s" % (
			self.path,
			record_name)

		record_data = self.client.get_yaml (
			"%s/data" % record_key)

		return record_data

	def exists_file (self, record_name, file_name):

		record_key = "%s/%s" % (
			self.path,
			record_name)

		return self.client.exists (
			key = "%s/%s" % (record_key, file_name))

	def get_file (self, record_name, file_name):

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

	def get_all_values (self):

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

	def get_all_list (self):

		if not self.client.exists (self.path):
			return []

		ret = []

		for record_key, record_yaml \
		in self.client.get_tree (self.path):

			if not record_key.endswith ("/data"):
				continue

			record_name = record_key [1:-5]

			record_data = yamlx.parse (record_yaml)

			ret.append ((record_name, record_data))

		return ret

	def get_all_dictionary (self):

		if not self.client.exists (self.path):
			return {}

		ret = {}

		for record_key, record_yaml \
		in self.client.get_tree (self.path):

			if not record_key.endswith ("/data"):
				continue

			record_name = record_key [1:-5]

			record_data = yamlx.parse (record_yaml)

			ret [record_name] = record_data

		return ret

	def to_yaml (self, record_data):

		return yamlx.encode (
			self.schema,
			record_data)

	def exists (self, record_name):

		record_key = "%s/%s" % (
			self.path,
			record_name)

		return self.client.exists (
			record_key)

# ex: noet ts=4 filetype=yaml
