from __future__ import absolute_import

schemas = dict ()

class Schema:

	def __init__ (self, groups):

		self.groups = groups

class SchemaField:

	def __init__ (
			self,
			name,
			required = False,
			default = None,
			sub_schema = None):

		self.name = name
		self.required = required
		self.default = default
		self.sub_schema = sub_schema

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

	def __getitem__ (self, name):

		return self.schemas [name]

# ex: noet ts=4 filetype=yaml
