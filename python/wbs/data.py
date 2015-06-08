from __future__ import absolute_import
from __future__ import unicode_literals

immutable_types = set ((int, str))

class Frozen (object):

	def __init__ (self, value):

		self._value = value

	def __getattribute__(self, name):

		if name == "_value":
			return super (Frozen, self).__getattribute__ (name)

		else:
			return freeze (getattr (self._value, name))

	def __setattr__ (self, name, value):

		if name == "_value":
			super (Frozen, self).__setattr__ (name, value)

		else:
			raise Exception (
				"Can't modify frozen object")

	def __iter__ (self):

		for item in self._value:
			yield freeze (item)

	def __getitem__ (self, key):

		return freeze (self._value [key])

def freeze (value):

	if value.__class__ in immutable_types:
		return value

	else:
		return Frozen (value)

# ex: noet ts=4 filetype=pyton
