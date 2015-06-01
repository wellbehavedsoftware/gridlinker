from __future__ import absolute_import
from __future__ import unicode_literals

schemas = dict ()

class Schema:

	def __init__ (self, groups):

		self.groups = groups

class SchemaField:

	def __init__ (
			self,
			name,
			type,
			required = False,
			default = None,
			sub_schema = None,
			values = None,
			help = None):

		self.name = name
		self.type = type
		self.required = required
		self.default = default
		self.sub_schema = sub_schema
		self.values = values
		self.help = help

class SchemaGroup:

	def __init__ (
			self,
			fields):

		self.fields = fields

class SchemaDatabase:

	def __init__ (self, source = None):

		if source:

			self.schemas = source.schemas.copy ()

		else:

			self.schemas = dict ()

	def define (self, name, groups):

		self.schemas [name] = Schema (groups)

	def read_all (self, all_data):

		for schema_name, schema_data in all_data.items ():
			self.read (schema_name, schema_data)

	def read (self, schema_name, schema_data):

		self.define (schema_name, [
			read_group (group_name, group_data)
			for group_name, group_data in schema_data.items ()
		])

	def __getitem__ (self, name):

		return self.schemas [name]

def read_group (group_name, group_data):

	return SchemaGroup ([
		read_field (field_name, field_data)
		for field_name, field_data in group_data.items ()
	])

def read_field (field_name, field_data):

	return SchemaField (
		name = field_name,
		required = field_data ["required"] == "yes",
		type = field_data ["type"],
		default = None,
		sub_schema = None)

# ex: noet ts=4 filetype=yaml
