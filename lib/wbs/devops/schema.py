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
			default = None):

		self.name = name
		self.required = required
		self.default = default		

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
