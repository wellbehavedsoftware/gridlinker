from __future__ import absolute_import
from __future__ import unicode_literals

import os
import importlib
import netaddr

from ansible.plugins.action import ActionBase

class ActionModule (ActionBase):

	TRANSFERS_FILES = False

	def __init__ (self, * arguments, ** keyword_arguments):

		self.support = importlib.import_module (
			os.environ ["GRIDLINKER_SUPPORT"]).support

		self.context = self.support.get_context ()

		self.client = self.context.client

		ActionBase.__init__ (
			self,
			* arguments,
			** keyword_arguments)

	def run (self, tmp = None, task_vars = dict ()):

		args = self._task.args

		database_location = args.get ("database_location")

		taken_ids = set ()

		for id_path, id_target \
		in self.client.get_tree (database_location):

			taken_ids.add (int (id_path [1:]))

		id_range = range (
			int (args ["first_id"]),
			int (args ["last_id"]))

		new_id = next (
			an_id for an_id in id_range
			if not an_id in taken_ids)

		allocation_name = args ["name"]

		self.client.create_raw (
			"%s/%s" % (database_location, str (new_id)),
			allocation_name)

		return dict (
			changed = True,
			new_id = new_id)

# ex: noet ts=4 filetype=python
