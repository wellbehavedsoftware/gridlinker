#!/usr/bin/python

from __future__ import absolute_import
from __future__ import unicode_literals

from ansible.module_utils.basic import *

def main ():

    module = AnsibleModule (
        argument_spec = { },
        check_invalid_arguments = False,
        supports_check_mode = False,
    )

    module.exit_json ()

main ()
