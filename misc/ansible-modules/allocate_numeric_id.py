#!/usr/bin/python

from __future__ import absolute_import
from __future__ import unicode_literals

import ipaddress

from ansible.module_utils.basic import *

def main ():

	module = AnsibleModule (
		argument_spec = dict (

			action = dict (
				default = "allocate",
				choices = [ "allocate", "release" ]),

			database_location = dict (
				required = True),

			first_id = dict (
				required = True),

			last_value = dict (
				required = True),

			name = dict (
				required = True),

		},

		check_invalid_arguments = True,
		supports_check_mode = False,

	)

	module.exit_json ()

main ()
