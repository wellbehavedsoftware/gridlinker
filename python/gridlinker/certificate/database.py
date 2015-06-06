from __future__ import absolute_import

from wbs import SchemaField, SchemaGroup

class CertificateDatabase:

	def __init__ (self, dnode_client, path, data):

		self.state = "none"

		self.dnode_client = dnode_client
		self.path = path
		self.data = data

	def exists (self):

		return self.dnode_client.exists (self.path + "/data")

	def create (self):

		if (self.state != "none"):
			raise Exception ()

		if self.dnode_client.exists (self.path + "/data"):
			raise Exception ()

		self.root_data = dict ({})

		self.root_data ["database_state"] = "active"

		self.dnode_client.set_yaml (
			"certificate-database",
			self.path + "/data",
			self.root_data)

	def load (self):

		# nothing much to do at the moment

		pass

	def request (self, name):

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

		request_csr.sign (request_key, "sha256")

		# dump to pem

		request_csr_string = crypto.dump_certificate_request (
			crypto.FILETYPE_PEM,
			request_csr)

		request_key_string = crypto.dump_privatekey (
			crypto.FILETYPE_PEM,
			request_key)

		# write to database

		request_path = self.path + "/" + name

		if self.dnode_client.exists (request_path + "/pending"):

			return (False, None, None)

		self.dnode_client.set_raw (
			request_path + "/pending/request",
			request_csr_string)

		self.dnode_client.set_raw (
			request_path + "/pending/key",
			request_key_string)

		return (
			True,
			request_csr_string,
			request_key_string,
		)

	def cancel (self, name):

		request_path = self.path + "/" + name

		# sanity check

		if not self.dnode_client.exists (request_path + "/pending"):

			return False

		# read pending

		request_csr_string = self.dnode_client.get_raw (
			request_path + "/pending/request")

		request_key_string = self.dnode_client.get_raw (
			request_path + "/pending/key")

		# create cancelled

		cancelled_path, cancelled_index = self.dnode_client.make_queue_dir (
			request_path + "/cancelled")

		self.dnode_client.set_raw (
			cancelled_path + "/request",
			request_csr_string)

		self.dnode_client.set_raw (
			cancelled_path + "/key",
			request_key_string)

		# remove pending

		self.dnode_client.rm_raw (
			request_path + "/pending/request")

		self.dnode_client.rm_raw (
			request_path + "/pending/key")

		self.dnode_client.rmdir_raw (
			request_path + "/pending")

		return True

	def signed (self,
			name,
			certificate_strings,
			verify_subject,
			verify_common_name):

		request_path = self.path + "/" + name

		# sanity check

		if not self.dnode_client.exists (request_path + "/pending"):

			raise Error ("No request pending")

		# read pending

		request_csr_string = self.dnode_client.get_raw (
			request_path + "/pending/request")

		request_key_string = self.dnode_client.get_raw (
			request_path + "/pending/key")

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

		if self.dnode_client.exists (request_path + "/current"):

			raise Exception ("TODO need to move chain somehow")

			# read current

			archive_csr_string = self.dnode_client.get_raw (
				request_path + "/current/request")

			archive_certificate_string = self.dnode_client.get_raw (
				request_path + "/current/certificate")

			archive_key_string = self.dnode_client.get_raw (
				request_path + "/current/key")

			# write to archive

			archive_path, archive_index = self.dnode_client.make_queue_dir (
				request_path + "/archive")

			self.dnode_client.set_raw (
				archive_path + "/request",
				archive_csr_string)

			self.dnode_client.set_raw (
				archive_path + "/certificate",
				archive_certificate_string)

			self.dnode_client.set_raw (
				archive_path + "/key",
				archive_key_string)

			# remove current

			self.dnode_client.rm_raw (
				request_path + "/current/request")

			self.dnode_client.rm_raw (
				request_path + "/current/certificate")

			self.dnode_client.rm_raw (
				request_path + "/current/key")

			self.dnode_client.rmdir_raw (
				request_path + "/current")

		# store new certificate

		self.dnode_client.set_raw (
			request_path + "/current/request",
			request_csr_string)

		self.dnode_client.set_raw (
			request_path + "/current/key",
			request_key_string)

		self.dnode_client.set_raw (
			request_path + "/current/certificate",
			certificate_strings [0])

		for chain_index, chain_string \
			in enumerate (certificate_strings [1:]):

			self.dnode_client.set_raw (
				request_path + "/current/chain/" + str (chain_index),
				chain_string)

		# remove pending

		self.dnode_client.rm_raw (
			request_path + "/pending/request")

		self.dnode_client.rm_raw (
			request_path + "/pending/key")

		self.dnode_client.rmdir_raw (
			request_path + "/pending")

	def get (self, name):

		entry_path = "%s/%s" % (
			self.path,
			name,
		)

		if not self.dnode_client.exists (
			entry_path):

			raise Exception (
				"No certificate for " + name)

		if not self.dnode_client.exists (
			entry_path):

			raise Exception (
				"No current certificate for " + name)

		certificate_strings = []

		certificate_strings.append (
			self.dnode_client.get_raw (
				entry_path + "/current/certificate"))

		for chain_index in range (0, 999):

			if not self.dnode_client.exists (
				entry_path + "/current/chain/" + str (chain_index)):

				break

			certificate_strings.append (
				self.dnode_client.get_raw (
					entry_path + "/current/chain/" + str (chain_index)))

		key_string = self.dnode_client.get_raw (
			entry_path + "/current/key")

		return (
			True,
			certificate_strings,
			key_string,
		)

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

	args_create (next_sub_parsers)
	args_request (next_sub_parsers)
	args_cancel (next_sub_parsers)
	args_signed (next_sub_parsers)
	args_export (next_sub_parsers)

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
		context.client,
		"/certificate/" + args.database,
		context.certificate_data)

	if database.exists ():

		print ("Certificate database already exists")

		return

	database.create ()

	print ("Certificate database created")

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

def do_request (context, args):

	database = dnode.certificate.Database (
		context.client,
		"/certificate/" + args.database,
		context.certificate_data)

	success, csr, key = database.request (
		args.common_name)

	if success:

		print ("Request created for " + args.common_name)

		sys.exit (0)

	else:

		print ("There is already a request pending for " + args.common_name)

		sys.exit (1)

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

def do_signed (args):

	dnode_client = dnode.get_client ()

	database = dnode.certificate.Database (
		dnode_client,
		"/certificate/" + args.database,
		dnode.certificate_data)

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

def do_cancel (args):

	dnode_client = dnode.get_client ()

	database = dnode.certificate.Database (
		dnode_client,
		"/certificate/" + args.database,
		dnode.certificate_data)

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
		"--full-certificate-chain",
		help = "path to write full certificate chain to")

	parser.add_argument (
		"--private-key",
		help = "path to write private key to")

def do_export (context, args):

	database = dnode.certificate.Database (
		context.client,
		"/certificate/" + args.database,
		context.certificate_data)

	database.load ()

	success, certificate_strings, key_string = database.get (
		args.common_name)

	if success:

		if args.full_certificate_chain:

			with open (args.full_certificate_chain, "w") as file_handle:

				for certificate_string in certificate_strings:
					file_handle.write (certificate_string)

			print ("Wrote full chain to %s" % (
				args.full_certificate_chain))

		if args.private_key:

			with open (args.private_key, "w") as file_handle:

				file_handle.write (key_string)

			print ("Wrote private key to %s" % (
				args.private_key))

	else:

		print ("failure")
