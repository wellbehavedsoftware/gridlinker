from __future__ import absolute_import
from __future__ import unicode_literals

from wbs.random import *

class FilterModule (object):

    def filters (self):

        return {

			"generate_random": generate_random,

		}

# ex: noet ts=4 filetype=python
