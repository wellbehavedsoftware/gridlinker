from __future__ import absolute_import
from __future__ import unicode_literals

import random
import string

def generate_random (length, characters = string.ascii_lowercase):

	return "".join ([
		random.choice (string.ascii_lowercase)
		for _ in range (length)
	])

def generate_password ():

	return generate_random (20)

# ex: noet ts=4 filetype=yaml
