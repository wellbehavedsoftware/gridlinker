from __future__ import absolute_import

import itertools
import sys
import time

from OpenSSL import crypto

from gridlinker.certificate.certificate import Certificate

from wbs import print_table

from wbs import TableColumn

class CertificateDatabase:

	def __init__ (self, context, path, data):

		self.state = "none"

		self.context = context
		self.path = path
		self.data = data

		self.client = context.client
		self.schemas = context.schemas

	def exists (self):

		return self.client.exists (self.path + "/data")

	def create (self):

		if (self.state != "none"):
			raise Exception ()

		if self.client.exists (self.path):
			raise Exception ()

		if self.client.exists (self.path + "/data"):
			raise Exception ()

		self.root_data = dict ({})

		self.root_data ["database_state"] = "active"
		self.root_data ["database_format"] = "1"

		self.client.set_yaml (
			self.path + "/data",
			self.root_data,
			self.schemas ["certificate-database"])

		self.state = "active"

	def load (self):

		if (self.state != "none"):
			raise Exception ()

		if not self.client.exists (self.path):

			raise Exception (
				"No such certificate database")

		if not self.client.exists (self.path + "/data"):

			raise Exception (
				"No such certificate database")

		self.root_data = self.client.get_yaml (self.path + "/data")

		self.root_data.setdefault ("database_format", "0")

		if int (self.root_data ["database_format"]) < 1:

			raise Exception (
				"Database format '%s' is old, please upgrade" % (
					self.root_data ["database_format"]))

		if int (self.root_data ["database_format"]) > 1:

			raise Exception (
				"Database format '%s' is new, please update code" % (
					self.root_data ["database_format"]))

		self.state = self.root_data ["database_state"]

	def upgrade (self):

		if (self.state != "none"):
			raise Exception ()

		if not self.client.exists (self.path):
			raise Exception ()

		if not self.client.exists (self.path + "/data"):
			raise Exception ()

		self.root_data = self.client.get_yaml (self.path + "/data")

		self.root_data.setdefault ("database_state", "active")
		self.root_data.setdefault ("database_format", "0")

		if int (self.root_data ["database_format"]) < 1:
			self.upgrade_1 ()

		self.state = self.root_data ["database_state"]

	def upgrade_1 (self):

		print "Upgrading database to version 1"

		# move certificates to new location

		for key in sorted (self.client.ls (self.path)):

			if key in [
				"data",
				"subjects",
				"indexes",
			]:
				continue

			print "  - %s" % key

			subject_path_old = self.path + "/" + key
			subject_path_new = self.path + "/subjects/" + key

			subject_data = self.client.get_tree (subject_path_old)

			for subject_key, subject_value in subject_data:

				self.client.set_raw (
					subject_path_new + subject_key,
					subject_value)

			if self.client.exists (
				subject_path_old + "/current"):

				subject_certificate = crypto.load_certificate (
					crypto.FILETYPE_PEM,
					self.client.get_raw (
						subject_path_old + "/current/certificate"))

				subject_not_after = time.strftime (
					"%Y-%m-%dT%H:%M:%SZ",
					time.strptime (
						subject_certificate.get_notAfter (),
						"%Y%m%d%H%M%SZ"))

				self.client.set_raw (
					self.path + "/indexes/not-after/" + subject_not_after,
					key)

			self.client.rm_recursive (
				subject_path_old)

		# update root data

		self.root_data ["database_format"] = "1"

		self.client.set_yaml (
			self.path + "/data",
			self.root_data,
			self.schemas ["certificate-database"])

	def request (self, name, alt_names):

		if (self.state != "active"):
			raise Exception ()

		# check there is no existing request

		subject_path = self.path + "/subjects/" + name

		if self.client.exists (subject_path + "/pending"):

			raise Exception ("already exists")

		# create key

		request_key = crypto.PKey ()
		request_key.generate_key (crypto.TYPE_RSA, 2048)

		# create certificate

		request_csr = crypto.X509Req ()

		request_csr.set_pubkey (request_key)

		request_csr.set_version (2)

		request_csr.get_subject ().C = self.data ["country"]
		request_csr.get_subject ().ST = "NA"
		request_csr.get_subject ().L = self.data ["locality"]
		request_csr.get_subject ().O = self.data ["organization"]
		request_csr.get_subject ().CN = name

		if (alt_names):

			request_csr.add_extensions ([

				crypto.X509Extension (
					"subjectAltName",
					False,
					",".join (alt_names)),

			])

		request_csr.sign (request_key, "sha256")

		# dump to pem

		request_csr_string = crypto.dump_certificate_request (
			crypto.FILETYPE_PEM,
			request_csr)

		request_key_string = crypto.dump_privatekey (
			crypto.FILETYPE_PEM,
			request_key)

		# write to database

		if self.client.exists (subject_path + "/pending"):
			return (False, None, None)

		self.client.set_raw (
			subject_path + "/pending/request",
			request_csr_string)

		self.client.set_raw (
			subject_path + "/pending/key",
			request_key_string)

		return (
			True,
			request_csr_string,
			request_key_string,
		)

	def cancel (self, name):

		if (self.state != "active"):
			raise Exception ()

		subject_path = self.path + "/" + name

		# sanity check

		if not self.client.exists (subject_path + "/pending"):

			return False

		# read pending

		request_csr_string = self.client.get_raw (
			subject_path + "/pending/request")

		request_key_string = self.client.get_raw (
			subject_path + "/pending/key")

		# create cancelled

		cancelled_path, cancelled_index = self.client.mkdir_queue (
			subject_path + "/cancelled")

		self.client.set_raw (
			cancelled_path + "/request",
			request_csr_string)

		self.client.set_raw (
			cancelled_path + "/key",
			request_key_string)

		# remove pending

		self.client.rm (
			subject_path + "/pending/request")

		self.client.rm (
			subject_path + "/pending/key")

		self.client.rmdir (
			subject_path + "/pending")

		return True

	def signed (self,
			name,
			certificate_strings,
			verify_subject,
			verify_common_name):

		if (self.state != "active"):
			raise Exception ()

		subject_path = self.path + "/subjects/" + name

		# sanity check

		if not self.client.exists (subject_path + "/pending"):

			raise Exception ("No request pending")

		# read pending

		request_csr_string = self.client.get_raw (
			subject_path + "/pending/request")

		request_key_string = self.client.get_raw (
			subject_path + "/pending/key")

		request_csr = crypto.load_certificate_request (
			crypto.FILETYPE_PEM,
			request_csr_string)

		request_key = crypto.load_privatekey (
			crypto.FILETYPE_PEM,
			request_key_string)

		# read chain

		certificates = [

			crypto.load_certificate (
				crypto.FILETYPE_PEM,
				certificate_string)

			for certificate_string
				in certificate_strings

		]

		# verify chain

		if not request_csr.verify (certificates [0].get_pubkey ()):

			raise Exception (
				"Public key of certificate does not match request")

		if verify_subject \
		and request_csr.get_subject () \
			!= certificates [0].get_subject ():

			raise Exception (
				"Subject of certificate does not match request")

		if verify_common_name \
		and request_csr.get_subject ().CN \
			!= certificates [0].get_subject ().CN:

			raise Exception (
				"Common name of certificate does not match request")

		for child, parent in zip (
			certificates [:-1],
			certificates [1:]):

			if not child.get_issuer () == parent.get_subject ():

				raise Exception (
					"Certificate chain subjects and issues do not match")

		if certificates [-1].get_issuer () != certificates [-1].get_subject ():

			raise Exception (
				"Root certificate is not self-signed")

		# TODO verify the actual signatures of the chain

		# archive existing certificate

		if self.client.exists (subject_path + "/current"):

			# read current

			archive_csr_string = self.client.get_raw_or_none (
				subject_path + "/current/request")

			archive_certificate_string = self.client.get_raw (
				subject_path + "/current/certificate")

			archive_key_string = self.client.get_raw (
				subject_path + "/current/key")

			archive_certificate_chain_strings = self.client.get_list (
				subject_path + "/current/chain")

			# write to archive

			archive_path, archive_index = self.client.mkdir_queue (
				subject_path + "/archive")

			if archive_csr_string:

				self.client.set_raw (
					archive_path + "/request",
					archive_csr_string)

			self.client.set_raw (
				archive_path + "/certificate",
				archive_certificate_string)

			self.client.set_raw (
				archive_path + "/key",
				archive_key_string)

			for chain_index, chain_string \
				in enumerate (archive_certificate_chain_strings):

				self.client.set_raw (
					archive_path + "/chain/" + str (chain_index),
					chain_string)

			# remove current

			if archive_csr_string:

				self.client.rm (
					subject_path + "/current/request")

			self.client.rm (
				subject_path + "/current/certificate")

			self.client.rm (
				subject_path + "/current/key")

			self.client.rm_recursive (
				subject_path + "/current/chain")

			self.client.rmdir (
				subject_path + "/current")

		# store new certificate

		self.client.set_raw (
			subject_path + "/current/request",
			request_csr_string)

		self.client.set_raw (
			subject_path + "/current/key",
			request_key_string)

		self.client.set_raw (
			subject_path + "/current/certificate",
			certificate_strings [0])

		for chain_index, chain_string \
			in enumerate (certificate_strings [1:]):

			self.client.set_raw (
				subject_path + "/current/chain/" + str (chain_index),
				chain_string)

		subject_not_after = time.strftime (
			"%Y-%m-%dT%H:%M:%SZ",
			time.strptime (
				certificates [0].get_notAfter (),
				"%Y%m%d%H%M%SZ"))

		self.client.set_raw (
			self.path + "/indexes/not-after/" + subject_not_after,
			name)

		# remove pending

		self.client.rm (
			subject_path + "/pending/request")

		self.client.rm (
			subject_path + "/pending/key")

		self.client.rmdir (
			subject_path + "/pending")

	def import_existing (self,
			name,
			certificate_strings,
			private_key_string,
			verify_subject = True,
			verify_common_name = True):

		subject_path = self.path + "/" + name

		# read certificates and private key

		certificates = [

			crypto.load_certificate (
				crypto.FILETYPE_PEM,
				certificate_string)

			for certificate_string
				in certificate_strings

		]

		private_key = crypto.load_privatekey (
			crypto.FILETYPE_PEM,
			private_key_string)

		# verify chain

		try:

			test_string = "HELLO WORLD"
			test_hash = "sha512"

			crypto.verify (
				certificates [0],
				crypto.sign (
					private_key,
					test_string,
					test_hash),
				test_string,
				test_hash)

		except crypto.Error:

			raise Exception (
				"Private key and certificate do not match")

		if verify_common_name \
		and name != certificates [0].get_subject ().CN:

			raise Exception (
				"Common name of certificate does not match request")

		for child, parent in zip (
			certificates [:-1],
			certificates [1:]):

			if not child.get_issuer () == parent.get_subject ():

				raise Exception (
					"Certificate chain subjects and issues do not match")

		if certificates [-1].get_issuer () != certificates [-1].get_subject ():

			raise Exception (
				"Root certificate is not self-signed")

		# TODO verify the actual signatures of the chain

		# archive existing certificate

		if self.client.exists (subject_path + "/current"):

			raise Exception ("TODO need to move chain somehow")

			# read current

			archive_csr_string = self.client.get_raw (
				subject_path + "/current/request")

			archive_certificate_string = self.client.get_raw (
				subject_path + "/current/certificate")

			archive_key_string = self.client.get_raw (
				subject_path + "/current/key")

			# write to archive

			archive_path, archive_index = self.client.make_queue_dir (
				subject_path + "/archive")

			self.client.set_raw (
				archive_path + "/request",
				archive_csr_string)

			self.client.set_raw (
				archive_path + "/certificate",
				archive_certificate_string)

			self.client.set_raw (
				archive_path + "/key",
				archive_key_string)

			# remove current

			self.client.rm (
				subject_path + "/current/request")

			self.client.rm (
				subject_path + "/current/certificate")

			self.client.rm (
				subject_path + "/current/key")

			self.client.rmdir (
				subject_path + "/current")

		# store new certificate

		self.client.set_raw (
			subject_path + "/current/key",
			private_key_string)

		self.client.set_raw (
			subject_path + "/current/certificate",
			certificate_strings [0])

		for chain_index, chain_string \
			in enumerate (certificate_strings [1:]):

			self.client.set_raw (
				subject_path + "/current/chain/" + str (chain_index),
				chain_string)

		subject_not_after = time.strftime (
			"%Y-%m-%dT%H:%M:%SZ",
			time.strptime (
				certificates [0].get_notAfter (),
				"%Y%m%d%H%M%SZ"))

		self.client.set_raw (
			self.path + "/indexes/not-after/" + subject_not_after,
			name)

		# TODO data

	def get (self, name):

		if (self.state != "active"):
			raise Exception ()

		entry_path = self.path + "/subjects/" + name

		if not self.client.exists (
			entry_path):

			raise Exception (
				"No certificate for " + name)

		if not self.client.exists (
			entry_path):

			raise Exception (
				"No current certificate for " + name)

		certificate_path = entry_path + "/current/certificate"
		certificate_string = self.client.get_raw (certificate_path)

		chain_paths = []
		chain_strings = []

		for chain_index in range (0, 9):

			chain_path = entry_path + "/current/chain/" + str (chain_index)

			if not self.client.exists (chain_path):
				break

			chain_string = self.client.get_raw (chain_path)

			chain_strings.append (chain_string)
			chain_paths.append (chain_path)

		key_path = entry_path + "/current/key"
		key_string = self.client.get_raw (key_path)

		# convert to rsa private key
		# TODO backport this to pyopenssl

		private_key = crypto.load_privatekey (crypto.FILETYPE_PEM, key_string)

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

		# format other information

		subject_certificate = crypto.load_certificate (
			crypto.FILETYPE_PEM,
			certificate_string)

		subject_not_before = time.strftime (
			"%Y-%m-%dT%H:%M:%SZ",
			time.strptime (
				subject_certificate.get_notBefore (),
				"%Y%m%d%H%M%SZ"))

		subject_not_after = time.strftime (
			"%Y-%m-%dT%H:%M:%SZ",
			time.strptime (
				subject_certificate.get_notAfter (),
				"%Y%m%d%H%M%SZ"))

		# return

		return Certificate (

			common_name = name,

			serial = None,
			digest = None,

			request = None,

			certificate = certificate_string,
			certificate_path = certificate_path,

			not_before = subject_not_before,
			not_after = subject_not_after,

			chain = chain_strings,
			chain_paths = chain_paths,

			private_key = key_string,
			private_key_path = key_path,

			rsa_private_key = rsa_private_key_string)

	def get_all (self):

		if (self.state != "active"):
			raise Exception ()

		return [
			self.get (subject_name)
			for subject_name in self.client.ls (self.path + "/subjects")
		]

def args (prev_sub_parsers):

	parser = prev_sub_parsers.add_parser (
		name = "database",
		help = "manage a database of certificates",
		description = """
			This tool manages a database of certificates, along with their
			corresponding certificate chains and private keys. It is also able
			to generate certificate signing requests which are normally required
			when working with third-party certificate authorities.
		""")

	next_sub_parsers = parser.add_subparsers ()

	args_cancel (next_sub_parsers)
	args_create (next_sub_parsers)
	args_export (next_sub_parsers)
	args_import (next_sub_parsers)
	args_list (next_sub_parsers)
	args_request (next_sub_parsers)
	args_search (next_sub_parsers)
	args_signed (next_sub_parsers)
	args_upgrade (next_sub_parsers)

def args_create (sub_parsers):

	parser_create = sub_parsers.add_parser (
		"create",
		help = "create a new certificate database",
		description = """
			Create a new certificate database. This initialised the metadata for
			the certificate database and is required before issuing any other
			commands.
		""")

	parser_create.set_defaults (
		func = do_create)

	parser_create.add_argument (
		"--database",
		required = True,
		help = "name of certificate database to create")


def do_create (context, args):

	database = CertificateDatabase (
		context,
		"/certificate/" + args.database,
		context.certificate_data)

	if database.exists ():

		print ("Certificate database already exists")

		return

	database.create ()

	print ("Certificate database created")

def args_list (sub_parsers):

	parser = sub_parsers.add_parser (
		"list",
		help = "list all certificate databases",
		description = """
			This tool outputs a list of certificate databases which have been
			created, along with their name and basic information.
		""")

	parser.set_defaults (
		func = do_list)

def do_list (context, args):

	rows = []

	for name in context.client.ls ("/certificate"):

		authority = CertificateDatabase (
			context,
			"/certificate/" + name,
			context.certificate_data)

		rows.append (dict (
			name = name))

	rows.sort (key = lambda row: row ["name"])

	columns = [
		TableColumn ("name", "Name"),
	]

	print_table (columns, rows, sys.stdout)

def args_request (sub_parsers):

	parser = sub_parsers.add_parser (
		"request",
		help = "create a new certificate request",
		description = """
			Create a new certificate request. This creates a public/private
			keypair and a corresponding certificate request, which should be
			sent to a certificate authority to be signed. The certificate will
			be in the "pending" state. Once the signed certificate is received,
			use the "signed" command to import it and move it to the "current"
			state. It is possible to have a "pending" certificate request and a
			"current" signed certificate at the same time.
		""")

	parser.set_defaults (
		func = do_request)

	parser.add_argument (
		"--database",
		required = True,
		help = "name of certificate database to use")

	parser.add_argument (
		"--common-name",
		required = True,
		help = "common name of certificate request to create")

	parser.add_argument (
		"--print-request",
		required = False,
		action = "store_true",
		help = "print the pem encoded request to stdout")

	# alt names

	parser_alt_names = parser.add_argument_group (
		"alt names")

	parser_alt_names.add_argument (
		"--alt-dns",
		help = "alternative dns hostname",
		default = [],
		action = "append")

	parser_alt_names.add_argument (
		"--alt-ip",
		help = "alternative ip address",
		default = [],
		action = "append")

	parser_alt_names.add_argument (
		"--alt-email",
		help = "alternative email address",
		default = [],
		action = "append")

def do_request (context, args):

	database = CertificateDatabase (
		context,
		"/certificate/" + args.database,
		context.certificate_data)

	database.load ()

	alt_names = list (itertools.chain.from_iterable ([
		[ "DNS:" + alt_dns for alt_dns in args.alt_dns ],
		[ "IP:" + alt_ip for alt_ip in args.alt_ip ],
		[ "email:" + alt_email for alt_email in args.alt_email ],
	]))

	success, csr, key = database.request (
		args.common_name,
		alt_names)

	if success:

		print ("Request created for " + args.common_name)

		if args.print_request:

			print ("")
			print (csr)

		sys.exit (0)

	else:

		print ("There is already a request pending for " + args.common_name)

		sys.exit (1)

def args_search (sub_parsers):

	parser = sub_parsers.add_parser (
		"search",
		help = "search certificates in a database",
		description = """
			This tool outputs a list of certificates present in a database,
			according to various options to filter the included certificates,
			and the format and order to display them in.
		""")

	parser.set_defaults (
		func = do_search)

	parser.add_argument (
		"--database",
		required = True,
		help = "name of certificate database to search")

	parser_ordering = parser.add_argument_group (
		"ordering")

	parser_ordering_exclusive = (
		parser_ordering.add_mutually_exclusive_group ())

	parser_ordering_exclusive.add_argument (
		"--order-by-expiry",
		action = "store_const",
		const = "expiry",
		dest = "ordering",
		help = "sort by order of expiry")

def do_search (context, args):

	database = CertificateDatabase (
		context,
		"/certificate/" + args.database,
		context.certificate_data)

	database.load ()

	certificates = database.get_all ()

	rows = []

	for certificate in certificates:

		rows.append (dict (
			name = certificate.common_name,
			not_before = certificate.not_before,
			not_after = certificate.not_after))

	if args.ordering == None:

		rows.sort (key = lambda row: row ["name"])

	elif args.ordering == "expiry":

		rows.sort (key = lambda row: row ["not_after"])

	else:

		raise Exception ()

	columns = [
		TableColumn ("name", "Name"),
		TableColumn ("not_before", "Not before"),
		TableColumn ("not_after", "Not after"),
	]

	print_table (columns, rows, sys.stdout)

def args_import (sub_parsers):

	parser = sub_parsers.add_parser (
		"import",
		help = "import a complete certificate",
		description = """
			Import a signed certificate, which has been generated externally.
			This could be used to import certificates which already existed when
			the certificate database was created, or if a certificate needs to
			be generated by a third party along with the private key. You will
			need to repeat the --certificate option once for every certificate
			in the chain, starting with the certificate itself, and ending with
			the self-signed root certificate authority.
		""")

	parser.set_defaults (
		func = do_import)

	parser.add_argument (
		"--database",
		required = True,
		help = "name of certificate database to use")

	parser.add_argument (
		"--common-name",
		required = True,
		help = "common name of certificate to store")

	parser.add_argument (
		"--certificate",
		action = "append",
		required = True,
		help = "path to signed certificate file, specify once for each in chain")

	parser.add_argument (
		"--private-key",
		required = True,
		help = "path to private key")

	parser.add_argument (
		"--ignore-common-name-mismatch",
		action = "store_true",
		help = "unless set, the signed certificate common name must exactly match the one specified")

def do_import (context, args):

	database = CertificateDatabase (
		context,
		"/certificate/" + args.database,
		context.certificate_data)

	certificate_strings = []

	for certificate_filename in args.certificate:

		with open (certificate_filename) as file_handle:

			certificate_strings.append (
				file_handle.read ())

	with open (args.private_key) as file_handle:

		private_key_string = file_handle.read ()

	database.import_existing (
		args.common_name,
		certificate_strings,
		private_key_string,
		not args.ignore_common_name_mismatch)

	print ("Certificate imported for " + args.common_name)

	sys.exit (0)

def args_signed (sub_parsers):

	parser = sub_parsers.add_parser (
		"signed",
		help = "import a signed certificate to complete a pending request",
		description = """
			Import a signed certificate, to complete a pending request. Use this
			command following a "request" command, once the request has been
			signed by a certificate authority, and the certificate has been
			granted. This updates a certificate in the "pending" state and makes
			it "current". You will need to repeat the --certificate option once
			for every certificate in the chain, starting with the certificate
			which matches the request, and ending with the self-signed root
			certificate authority.
		""")

	parser.set_defaults (
		func = do_signed)

	parser.add_argument (
		"--database",
		required = True,
		help = "name of certificate database to use")

	parser.add_argument (
		"--common-name",
		required = True,
		help = "common name of pending certificate request to sign")

	parser.add_argument (
		"--certificate",
		action = "append",
		required = True,
		help = "path to signed certificate file, specify once for each in chain")

	parser.add_argument (
		"--ignore-subject-mismatch",
		action = "store_true",
		help = "unless set, the signed certificate subject must exactly match the request")

	parser.add_argument (
		"--ignore-common-name-mismatch",
		action = "store_true",
		help = "unless set, the signed certificate common name must exactly match the request")

def do_signed (context, args):

	database = CertificateDatabase (
		context,
		"/certificate/" + args.database,
		context.certificate_data)

	database.load ()

	certificate_strings = []

	for certificate_filename in args.certificate:

		with open (certificate_filename) as file_handle:

			certificate_strings.append (
				file_handle.read ())

	database.signed (
		args.common_name,
		certificate_strings,
		not args.ignore_subject_mismatch,
		not args.ignore_common_name_mismatch)

	print ("Request signed for " + args.common_name)

	sys.exit (0)

def args_cancel (sub_parsers):

	parser = sub_parsers.add_parser (
		"cancel",
		help = "cancel a pending request",
		description = """
			Cancel a pending request. Use this if a certificate request which is
			in the "pending" state is never going to be signed, for example if
			the information is incorrect and it needs to be created again.
		""")

	parser.set_defaults (
		func = do_cancel)

	parser.add_argument (
		"--database",
		required = True,
		help = "name of certificate database to use")

	parser.add_argument (
		"--common-name",
		required = True,
		help = "common name of pending certificate request to cancel")

def do_cancel (context, args):

	database = CertificateDatabase (
		context,
		"/certificate/" + args.database,
		context.certificate_data)

	success = database.cancel (
		args.common_name)

	if success:

		print ("Request cancelled for " + args.common_name)

		sys.exit (0)

	else:

		print ("There is no request pending for " + args.common_name)

		sys.exit (1)

def args_export (sub_parsers):

	parser = sub_parsers.add_parser (
		"export",
		help = "export a certificate, chain, and/or key to the filesystem")

	parser.set_defaults (
		func = do_export)

	parser.add_argument (
		"--database",
		required = True,
		help = "name of certificate database to use")

	parser.add_argument (
		"--common-name",
		required = True,
		help = "common name of certificate request to export")

	parser.add_argument (
		"--certificate",
		help = "path to write certificate to")

	parser.add_argument (
		"--certificate-chain",
		help = "path to write rest of certificate chain to")

	parser.add_argument (
		"--full-certificate-chain",
		help = "path to write full certificate chain to")

	parser.add_argument (
		"--ca-certificate",
		help = "path to write ca certificate to")

	parser.add_argument (
		"--private-key",
		help = "path to write private key to")

	parser.add_argument (
		"--rsa-private-key",
		help = "path to write rsa private key")

	parser.add_argument (
		"--print-request",
		action = "store_true",
		help = "print signing request to stdout")

def do_export (context, args):

	database = CertificateDatabase (
		context,
		"/certificate/" + args.database,
		context.certificate_data)

	database.load ()

	certificate = database.get (
		args.common_name)

	if args.certificate:

		with open (args.certificate, "w") as file_handle:
			file_handle.write (certificate.certificate)

		print ("Wrote certificate to %s" % (
			args.certificate))

	if args.certificate_chain:

		with open (args.certificate_chain, "w") as file_handle:

			for chain in certificate.chain:
				file_handle.write (chain)

		print ("Wrote certificate chain to %s" % (
			args.certificate_chain))

	if args.full_certificate_chain:

		with open (args.full_certificate_chain, "w") as file_handle:

			file_handle.write (certificate.certificate)

			for chain in certificate.chain:
				file_handle.write (chain)

		print ("Wrote full certificate chain to %s" % (
			args.full_certificate_chain))

	if args.ca_certificate:

		with open (args.ca_certificate, "w") as file_handle:
			file_handle.write (certificate.chain [-1])

		print ("Wrote ca certificate to %s" % (
			args.ca_certificate))

	if args.private_key:

		with open (args.private_key, "w") as file_handle:
			file_handle.write (certificate.private_key)

		print ("Wrote private key to %s" % (
			args.private_key))

	if args.rsa_private_key:

		with open (args.rsa_private_key, "w") as file_handle:
			file_handle.write (certificate.rsa_private_key)

		print ("Wrote RSA private key to %s" % (
			args.rsa_private_key))

	if args.print_request:

		print ("TODO")

def args_upgrade (sub_parsers):

	parser_upgrade = sub_parsers.add_parser (
		"upgrade",
		help = "upgrade an existing certificate database",
		description = """
			Modifies the internal format of a certificate database, converting
			it from an old version to the current one. This is a required
			operation whenever the code is updated to use a new database format.
		""")

	parser_upgrade.set_defaults (
		func = do_upgrade)

	parser_upgrade.add_argument (
		"--database",
		required = True,
		help = "name of certificate database to upgrade")


def do_upgrade (context, args):

	database = CertificateDatabase (
		context,
		"/certificate/" + args.database,
		context.certificate_data)

	if not database.exists ():

		print (
			"Certificate database '%s' does not exist" % (
				args.database))

		return

	database.upgrade ()

	print (
		"Database format is the latest version")

# ex: noet ts=4 filetype=python
