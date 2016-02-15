from __future__ import absolute_import
from __future__ import unicode_literals

import os
import importlib

from ansible.plugins.action import ActionBase

from gridlinker import CertificateAuthority

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

		authority_name = self._task.args.get ("authority")
		common_name = self._task.args.get ("common_name")

		authority_path = "/authority/%s" % authority_name

		if self.client.exists (authority_path):
			
			return dict (
				changed = False)

		authority = CertificateAuthority (
			self.context,
			authority_path,
			self.context.certificate_data)

		authority.create (common_name)

		return dict (
			changed = True)

# ex: noet ts=4 filetype=python
