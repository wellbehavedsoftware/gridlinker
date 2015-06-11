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

		for key, value in complex_args.items ():

			dynamic_path = template.template (self.runner.basedir, key, inject)

			if not "." in dynamic_path:
				raise Exception ()

			prefix, rest = dynamic_path.split (".", 2)

			resource_data.setdefault (prefix, {})
			resource_data [prefix] [rest] = value

			options [prefix] = resource_data [prefix]
			options [prefix + "_" + rest] = value

		self.context.resources.set (resource_name, resource_data)

		return ReturnData (

			conn = conn,
			result = dict (
				ansible_facts = options))
