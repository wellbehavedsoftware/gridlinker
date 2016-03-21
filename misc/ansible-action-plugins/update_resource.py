from __future__ import absolute_import
from __future__ import unicode_literals

import importlib
import os

from ansible.plugins.action import ActionBase

class ActionModule (ActionBase):

	TRANSFERS_FILES = False

	def __init__ (self, * arguments, ** keyword_arguments):

		self.support = importlib.import_module (
			os.environ ["GRIDLINKER_SUPPORT"]).support

		self.context = self.support.get_context ()

		ActionBase.__init__ (
			self,
			* arguments,
			** keyword_arguments)

	def run (self, tmp = None, task_vars = dict ()):

		options = {}

		resource_name = task_vars.get ("inventory_hostname")

		if not self.context.resources.exists_slow (resource_name):
			raise Exception ("Not found: " + resource_name)

		resource_data = (
			self.context.resources.get_slow (resource_name))

		changed = False

		for key, value in self._task.args.items ():

			dynamic_path = (
				self._templar.template (
					key))

			if not "." in dynamic_path:

				raise Exception (
					"Invalid path for update_resource: %s" % dynamic_path)

			prefix, rest = (
				dynamic_path.split (".", 2))

			resource_vars = (
				task_vars ["hostvars"] [resource_name])

			options.setdefault (
				prefix,
				resource_vars.get (prefix, {}))

			if rest in options [prefix] \
			and options [prefix] [rest] == value:
				continue

			changed = True

			resource_data.setdefault (prefix, {})
			resource_data [prefix] [rest] = value

			options [prefix] [rest] = value
			options [prefix + "_" + rest] = value

		self.context.resources.set (resource_name, resource_data)

		return dict (
			ansible_facts = options,
			changed = changed)

# ex: noet ts=4 filetype=python
