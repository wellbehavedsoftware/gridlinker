from __future__ import absolute_import
from __future__ import unicode_literals

import os
import importlib

from ansible import utils
from ansible.runner.return_data import ReturnData
from ansible.utils import template

from gridlinker import CertificateAuthority

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

		authority_name = complex_args ["authority"]
		common_name = complex_args ["common_name"]

		authority_path = "/authority/%s" % authority_name

		if self.client.exists (authority_path):
			
			return ReturnData (
				conn = conn,
				result = dict (
					changed = False))

		authority = CertificateAuthority (
			self.context,
			authority_path,
			self.context.certificate_data)

		authority.create (common_name)

		return ReturnData (
			conn = conn,
			result = dict (
				changed = True))

# ex: noet ts=4 filetype=python
