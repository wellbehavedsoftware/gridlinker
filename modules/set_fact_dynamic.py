#!/usr/bin/python

from ansible.module_utils.basic import *

def main ():

    module = AnsibleModule (
        argument_spec = { },
        check_invalid_arguments = False,
        supports_check_mode = False,
    )

    module.exit_json ()

main ()
