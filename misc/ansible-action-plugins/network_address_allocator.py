from __future__ import absolute_import
from __future__ import unicode_literals

import os
import importlib
import netaddr

#from ansible import utils
#from ansible.runner.return_data import ReturnData
#from ansible.utils import template

from ansible.plugins.action import ActionBase

class ActionModule (ActionBase):

	TRANSFERS_FILES = False

	def __init__ (self, * arguments, ** keyword_arguments):

		self.support = (
			importlib.import_module (
				os.environ ["GRIDLINKER_SUPPORT"]
			).support
		)

		self.context = (
			self.support.get_context ())

		self.client = (
			self.context.client)

		ActionBase.__init__ (
			self,
			* arguments,
			** keyword_arguments)

	def run (self, tmp = None, task_vars = dict ()):

		database_location = self._task.args.get ("database_location")

		taken_addresses = set ()

		for ip_path, ip_target \
		in self.client.get_tree (database_location):

			ip_name = ip_path [1:]
			taken_addresses.add (ip_name)

		address_range = (
			netaddr.iter_iprange (
				self._task.args.get ("start_address"),
				self._task.args.get ("end_address")))

		ip_address = next (
			ip_address for ip_address in address_range
			if not str (ip_address) in taken_addresses)

		allocation_name = (
			self._task.args.get ("name"))

		self.client.create_raw (
			"%s/%s" % (database_location, str (ip_address)),
			allocation_name)

		return dict (
			changed = True,
			address = ip_address)

# ex: noet ts=4 filetype=python
