from __future__ import absolute_import
from __future__ import unicode_literals

import importlib
import os

from ansible import utils
from ansible.runner.return_data import ReturnData
from ansible.utils import template

class ActionModule (object):

	TRANSFERS_FILES = False

	def __init__ (self, runner):

		self.runner = runner

		self.support = importlib.import_module (os.environ ["GRIDLINKER_SUPPORT"]).support
		self.context = self.support.get_context ()

	def run (self,
		conn,
		tmp,
		module_name,
		module_args,
		inject,
		complex_args = {},
		** kwargs
	):

		options = {}

		resource_name = inject ["inventory_hostname"]

		if not self.context.resources.exists_slow (resource_name):
			raise Exception ("Not found: " + resource_name)

		resource_data = self.context.resources.get_slow (resource_name)

		changed = False

		for key, value in complex_args.items ():

			dynamic_path = template.template (self.runner.basedir, key, inject)

			if not "." in dynamic_path:

				raise Exception (
					"Invalid path for update_resource: %s" % dynamic_path)

			prefix, rest = dynamic_path.split (".", 2)

			options.setdefault (prefix, inject.get (prefix, {}))

			if rest in options [prefix] \
			and options [prefix] [rest] == value:
				continue

			changed = True

			resource_data.setdefault (prefix, {})
			resource_data [prefix] [rest] = value

			options [prefix] [rest] = value
			options [prefix + "_" + rest] = value

		self.context.resources.set (resource_name, resource_data)

		return ReturnData (
			conn = conn,
			result = dict (
				ansible_facts = options,
				changed = changed))

# ex: noet ts=4 filetype=python
