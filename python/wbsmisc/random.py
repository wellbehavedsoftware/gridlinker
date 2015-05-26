from __future__ import absolute_import

import random
import string

def generate_password ():

	return "".join (random.choice (
		string.ascii_lowercase
	) for _ in range (20))

# ex: noet ts=4 filetype=yaml
