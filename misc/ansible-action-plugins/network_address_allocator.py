from __future__ import absolute_import
from __future__ import unicode_literals

import os
import importlib
import netaddr

from ansible import utils
from ansible.runner.return_data import ReturnData
from ansible.utils import template

class ActionModule (object):

	TRANSFERS_FILES = False

	def __init__ (self, runner):

		self.runner = runner

		self.support = importlib.import_module (os.environ ["GRIDLINKER_SUPPORT"]).support
		self.context = self.support.get_context ()

		self.client = self.context.client

	def run (self,
		conn,
		tmp,
		module_name,
		module_args,
		inject,
		complex_args = {},
		** kwargs
	):

		database_location = complex_args ["database_location"]

		taken_addresses = set ()

		for ip_path, ip_target \
		in self.client.get_tree (database_location):

			ip_name = ip_path [1:]
			taken_addresses.add (ip_name)

		address_range = netaddr.iter_iprange (
			complex_args ["start_address"],
			complex_args ["end_address"])

		ip_address = next (
			ip_address for ip_address in address_range
			if not str (ip_address) in taken_addresses)

		allocation_name = complex_args ["name"]

		self.client.create_raw (
			"%s/%s" % (database_location, str (ip_address)),
			allocation_name)

		return ReturnData (
			conn = conn,
			result = dict (
				changed = True,
				address = ip_address))

# ex: noet ts=4 filetype=python
