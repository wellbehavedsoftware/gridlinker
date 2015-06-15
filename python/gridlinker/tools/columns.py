from __future__ import absolute_import
from __future__ import unicode_literals

class SimpleColumn (object):

	def __init__ (self, section, name, label, default):

		self.section = section
		self.name = name
		self.label = label
		self.default = default

	def exists (self, context, helper, record_data):

		if not self.section in record_data:
			return False

		if not self.name in record_data [self.section]:
			return False

		return True

	def get (self, context, helper, record_data):

		return record_data [self.section] [self.name]

class UniqueNameColumn (object):

	def __init__ (self):

		self.name = "unique_name"
		self.label = "Unique name"
		self.default = True

	def exists (self, context, helper, record_data):

		return True

	def get (self, context, helper, record_data):

		return helper.existing_unique_name (context, record_data)
