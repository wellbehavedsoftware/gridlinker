#!/usr/bin/python

from __future__ import absolute_import
from __future__ import unicode_literals

from ansible.module_utils.basic import *

def main ():

	module = AnsibleModule (
		argument_spec = dict (

			authority = dict (
				required = True),

			common_name = dict (
				required = True),

			usage = dict (
				required = True,
				choices = [ "client", "server", "mixed" ]),

			alt_dns = dict (
				default = []),

			alt_ip = dict (
				default = []),

			alt_email = dict (
				default = []),

		},
		check_invalid_arguments = True,
		supports_check_mode = True
	)

	module.exit_json ()

main ()
