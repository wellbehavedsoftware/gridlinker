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
