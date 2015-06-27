from __future__ import absolute_import
from __future__ import unicode_literals

import os
import importlib
import itertools

from ansible import utils
from ansible.runner.return_data import ReturnData
from ansible.utils import template

from gridlinker import AlreadyExistsError
from gridlinker import CertificateAuthority

class ActionModule (object):

	TRANSFERS_FILES = False

	def __init__ (self, runner):

		self.runner = runner

		self.support = importlib.import_module (os.environ ["GRIDLINKER_SUPPORT"]).support

	def context (self):

		return self.support.get_context ()

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
		usage = complex_args ["usage"]
		alt_dns = complex_args.get ("alt_dns", [])
		alt_ip = complex_args.get ("alt_ip", [])
		alt_email = complex_args.get ("alt_email", [])

		authority_path = "/authority/%s" % authority_name

		authority = self.context ().authorities [authority_name]

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

			return ReturnData (
				conn = conn,
				result = dict (
					changed = False))

		return ReturnData (
			conn = conn,
			result = dict (
				changed = True,
				certificate = certificate.certificate_path,
				private_key = certificate.private_key_path))

# ex: noet ts=4 filetype=python
