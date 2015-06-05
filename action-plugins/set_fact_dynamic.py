from __future__ import absolute_import
from __future__ import unicode_literals

from ansible import utils
from ansible.runner.return_data import ReturnData
from ansible.utils import template

class ActionModule (object):

	TRANSFERS_FILES = False

	def __init__ (self, runner):

		self.runner = runner

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

		for key, value in complex_args.items ():

			dynamic_path = template.template (self.runner.basedir, key, inject)
			options [dynamic_path] = value

			dynamic_key = dynamic_path.replace ('.', '_')
			options [dynamic_key] = value

		return ReturnData (

			conn = conn,
				result = dict (
				ansible_facts = options))
