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

def env_combine (* envs):

	ret = {}

	for some_env in envs:

		for key, value in some_env.items ():

			if isinstance (value, list):

				if not key in ret:
					ret [key] = []

				if not isinstance (ret [key], list):
					raise Exception ()

				ret [key].extend (value)

			elif isinstance (value, str):

				ret [key] = value

			elif isinstance (value, unicode):

				ret [key] = value

			else:

				raise Exception ()

	return ret

def env_resolve (start, env):

	ret = {}

	for key, value in start.items ():

		ret [key] = value

	for key, value in env.items ():

		if isinstance (value, list):

			if key in ret:
				ret [key] = ":".join (value) + ":" + ret [key]

			else:
				ret [key] = ":".join (value)

		else:
			ret [key] = value

	return ret
