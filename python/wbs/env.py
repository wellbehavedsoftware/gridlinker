from __future__ import absolute_import
from __future__ import unicode_literals

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

# ex: noet ts=4 filetype=yaml
