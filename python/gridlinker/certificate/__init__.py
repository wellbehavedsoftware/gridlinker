from __future__ import absolute_import

from gridlinker.certificate.authority import CertificateAuthority
from gridlinker.certificate.certificate import Certificate
from gridlinker.certificate.database import CertificateDatabase

modules = [
	authority,
	certificate,
	database,
]

def args (prev_sub_parsers):

	parser = prev_sub_parsers.add_parser (
		"certificate",
		help = "manage x509 certificates and authorities",
		description = """
			This group of commands can be used to manage x509 certificates. The
			"authority" function can be used to run a certificate authority. The
			"database" command can be used to manage certificates which are
			signed elsewhere.
		""")

	next_sub_parsers = parser.add_subparsers ()

	for module in modules:
		module.args (next_sub_parsers)

# ex: noet ts=4 filetype=python
