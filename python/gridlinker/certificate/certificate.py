from __future__ import absolute_import

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
