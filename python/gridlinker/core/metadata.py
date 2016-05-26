from __future__ import absolute_import
from __future__ import unicode_literals

import collections
import yaml

def load (home):

	# load data

	with open ("%s/data/project" % home) as file_handle:

		metadata = collections.defaultdict (
			dict,
			yaml.load (file_handle))

	# return
	
	return metadata

# ex: noet ts=4 filetype=yaml
