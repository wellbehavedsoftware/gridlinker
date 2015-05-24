from __future__ import absolute_import

from wbsdevops.certificate.authority import CertificateAuthority
from wbsdevops.certificate.certificate import Certificate
from wbsdevops.certificate.database import CertificateDatabase

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

	authority.args (next_sub_parsers)
	certificate.args (next_sub_parsers)
	database.args (next_sub_parsers)

def schemas (schemas):

	authority.schemas (schemas)
	certificate.schemas (schemas)
	database.schemas (schemas)
