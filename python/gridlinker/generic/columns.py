from __future__ import absolute_import
from __future__ import unicode_literals

class SimpleColumn (object):

	def __init__ (self, section, name, label, default):

		self.section = section
		self.name = name
		self.label = label
		self.default = default
