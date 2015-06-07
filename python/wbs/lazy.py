from __future__ import absolute_import
from __future__ import unicode_literals

class lazy_property (object):

	def __init__ (self, getter):

		self.getter = getter
		self.name = getter.__name__

	def __get__ (self, target, target_class):

		if target is None:
			return None

		value = self.getter (target)

		setattr (
			target,
			self.name,
			value)

		return value

class LazyDictionary:

	def __init__ (self, init_function):

		self.init_function = init_function

		self.dict = dict ()

	def __getitem__ (self, key):

		if key in self.dict:
			return self.dict [key]

		else:
			value = self.init_function (key)
			self.dict [key] = value
			return value

# ex: noet ts=4 filetype=python
