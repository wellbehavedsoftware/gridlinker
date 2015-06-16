from __future__ import absolute_import
from __future__ import unicode_literals

import collections

immutable_types = set ([ int, str, unicode ])

class Frozen (object):

	acceptable_attributes = set ([
		"_value",
	])

	def __init__ (self, value):

		self._value = value

	def __getattribute__(self, name):

		if name in Frozen.acceptable_attributes:
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

	def __str__ (self):

		return str (self._value)

class FrozenList (list):

	acceptable_attributes = set ([
		"_value",
	])

	def __init__ (self, value):

		self._value = value

	def __getattribute__(self, name):

		if name in FrozenList.acceptable_attributes:
			return super (FrozenList, self).__getattribute__ (name)

		else:
			return freeze (getattr (self._value, name))

	def __setattr__ (self, name, value):

		if name == "_value":
			super (FrozenList, self).__setattr__ (name, value)

		else:
			raise Exception (
				"Can't modify frozen list")

	def __iter__ (self):

		for item in self._value:
			yield freeze (item)

	def __getitem__ (self, key):

		return freeze (self._value [key])

	def get (self, key, default):

		return freeze (self._value.get (key, default))

	def __str__ (self):

		return str (self._value)

class FrozenDict (dict):

	acceptable_attributes = set ([
		"_value",
		"__class__",
		"get",
		"keys",
		"items",
		"values",
	])

	def __init__ (self, value):

		self._value = value

	def __getattribute__(self, name):

		if name in FrozenDict.acceptable_attributes:
			return super (FrozenDict, self).__getattribute__ (name)

		else:
			return freeze (getattr (self._value, name))

	def __setattr__ (self, name, value):

		if name == "_value":
			super (FrozenDict, self).__setattr__ (name, value)

		else:
			raise Exception (
				"Can't modify frozen dictionary")

	# dictionary special methods

	def __len__ (self):

		return len (self._value)

	def __getitem__ (self, key):

		return freeze (self._value [key])

	def __setitem__ (self, key, value):

		raise Exception (
			"Can't modify frozen dictionary")

	def __delitem__ (self, key):

		raise Exception (
			"Can't modify frozen dictionary")

	def __iter__ (self):

		for item in self._value:
			yield freeze (item)

	def __reversed__ (self):

		raise Exception ("TODO")

	def __contains__ (self, item):

		return item in self._value

	def __missing__ (self, key):

		raise Exception ("TODO")

	# dictionary regular methods

	def get (self, key, default):

		return freeze (self._value.get (key, default))

	def keys (self):

		return [
			freeze (key)
			for key in self._value.keys ()
		]

	def items (self):

		return [
			(freeze (key), freeze (value))
			for key, value in self._value.items ()
		]

	def values (self):

		return [
			freeze (value)
			for value in self._value.values ()
		]

	def pop (self):

		raise Exception (
			"Can't modify frozen dictionary")

	def popitem (self):

		raise Exception (
			"Can't modify frozen dictionary")

	# other special methods

	def __str__ (self):

		return str (self._value)

class FrozenOrderedDict (collections.OrderedDict):

	acceptable_attributes = set ([
		"_value",
		"__class__",
		"get",
		"keys",
		"items",
		"values",
	])

	def __init__ (self, value):

		self._value = value

	def __getattribute__(self, name):

		if name in FrozenOrderedDict.acceptable_attributes:
			return super (FrozenOrderedDict, self).__getattribute__ (name)

		else:
			return freeze (getattr (self._value, name))

	def __setattr__ (self, name, value):

		if name == "_value":
			super (FrozenOrderedDict, self).__setattr__ (name, value)

		else:
			raise Exception (
				"Can't modify frozen dictionary")

	# dictionary special methods

	def __len__ (self):

		return len (self._value)

	def __getitem__ (self, key):

		return freeze (self._value [key])

	def __setitem__ (self, key, value):

		raise Exception (
			"Can't modify frozen dictionary")

	def __delitem__ (self, key):

		raise Exception (
			"Can't modify frozen dictionary")

	def __iter__ (self):

		for item in self._value:
			yield freeze (item)

	def __reversed__ (self):

		raise Exception ("TODO")

	def __contains__ (self, item):

		return item in self._value

	def __missing__ (self, key):

		raise Exception ("TODO")

	# dictionary regular methods

	def get (self, key, default):

		return freeze (self._value.get (key, default))

	def keys (self):

		return [
			freeze (key)
			for key in self._value.keys ()
		]

	def items (self):

		return [
			(freeze (key), freeze (value))
			for key, value in self._value.items ()
		]

	def values (self):

		return [
			freeze (value)
			for value in self._value.values ()
		]

	def pop (self):

		raise Exception (
			"Can't modify frozen dictionary")

	def popitem (self):

		raise Exception (
			"Can't modify frozen dictionary")

	# other special methods

	def __str__ (self):

		return str (self._value)

def freeze (value):

	if value.__class__ in immutable_types:
		return value

	elif isinstance (value, collections.OrderedDict):
		return FrozenOrderedDict (value)

	elif isinstance (value, dict):
		return FrozenDict (value)

	elif isinstance (value, list):
		return FrozenList (value)

	else:
		return Frozen (value)

def deep_copy (value):

	if isinstance (value, unicode):
		return value

	if isinstance (value, str):
		return value

	if isinstance (value, int):
		return value

	if isinstance (value, dict):

		return collections.OrderedDict ([
			(key, deep_copy (item))
			for key, item in value.items ()
		])

	if isinstance (value, list):

		return [
			deep_copy (item)
			for item in value
		]

	raise Exception ()

# ex: noet ts=4 filetype=pyton
