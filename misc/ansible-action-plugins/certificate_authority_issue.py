from __future__ import absolute_import
from __future__ import unicode_literals

import os
import importlib
import itertools

from ansible.plugins.action import ActionBase

from gridlinker import AlreadyExistsError
from gridlinker import CertificateAuthority

class ActionModule (ActionBase):

	TRANSFERS_FILES = False

	def __init__ (self, * arguments, ** keyword_arguments):

		self.support = importlib.import_module (
			os.environ ["GRIDLINKER_SUPPORT"]).support

		self.context = (
			self.support.get_context ())

		self.client = (
			self.context.client)

		ActionBase.__init__ (
			self,
			* arguments,
			** keyword_arguments)

	def run (self, tmp = None, task_vars = dict ()):

		authority_name = self._task.args.get ("authority")
		common_name = self._task.args.get ("common_name")
		usage = self._task.args.get ("usage")
		alt_dns = self._task.args.get ("alt_dns", [])
		alt_ip = self._task.args.get ("alt_ip", [])
		alt_email = self._task.args.get ("alt_email", [])

		authority_path = "/authority/%s" % authority_name

		authority = self.context.authorities [authority_name]

		alt_names = list (itertools.chain.from_iterable ([
			[ str ("DNS:" + item) for item in alt_dns ],
			[ str ("IP:" + item) for item in alt_ip ],
			[ str ("email:" + item) for item in alt_email ],
		]))

		try:

			certificate = authority.reissue (
				usage,
				common_name,
				alt_names)

		except AlreadyExistsError:

			return dict (
				changed = False)

		return dict (
			changed = True,
			certificate = certificate.certificate_path,
			private_key = certificate.private_key_path)

# ex: noet ts=4 filetype=python
