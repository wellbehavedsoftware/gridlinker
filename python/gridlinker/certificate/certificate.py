from __future__ import absolute_import
from __future__ import division
from __future__ import generators
from __future__ import nested_scopes
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import with_statement

import collections

Certificate = collections.namedtuple ("Certificate", [

	"serial",
	"digest",

	"certificate",
	"certificate_path",

	"chain",
	"chain_paths",

	"private_key",
	"private_key_path",

	"rsa_private_key",

])

class AlreadyExistsError (Exception):
	pass

class IllegalStateError (Exception):
	pass

# ex: noet ts=4 filetype=python
