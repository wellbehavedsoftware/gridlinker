from __future__ import absolute_import
from __future__ import unicode_literals

from wbs.random import *

class FilterModule (object):

    def filters (self):

        return {

			"generate_random": generate_random,
			"generate_mac_address": generate_mac_address,

		}

# ex: noet ts=4 filetype=python
