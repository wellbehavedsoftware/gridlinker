from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

def substring_before (value, separator):

	return value.partition (separator) [0]

def substring_after (value, separator):

	return value.partition (separator) [3]

class FilterModule (object):

    def filters (self):

        return {

			"substring_before": substring_before,
			"substring_after": substring_after,

		}

# ex: noet ts=4 filetype=python
