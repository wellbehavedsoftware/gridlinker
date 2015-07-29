from __future__ import absolute_import
from __future__ import division
from __future__ import generators
from __future__ import nested_scopes
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import with_statement

from OpenSSL import crypto, rand

def write_rsa_private_key (private_key):

	helper = crypto._PassphraseHelper (type, None)

	bio = crypto._new_mem_buf ()

	rsa_private_key = crypto._lib.EVP_PKEY_get1_RSA (private_key._pkey)

	result_code = crypto._lib.PEM_write_bio_RSAPrivateKey (
		bio,
		rsa_private_key,
		crypto._ffi.NULL,
		crypto._ffi.NULL,
		0,
		helper.callback,
		helper.callback_args)

	helper.raise_if_problem ()

	rsa_private_key_string = crypto._bio_to_string (bio)

	return rsa_private_key_string

# ex: noet ts=4 filetype=python
