from __future__ import absolute_import

import collections
import itertools
import re
import struct
import sys

from OpenSSL import crypto, rand

from wbsdevops.schema import SchemaField, SchemaGroup

serial_pattern = re.compile (
	r"^[1-9]\d*$")

digest_pattern = re.compile (
	r"^\d{2}(:\d{2})*$")

Certificate = collections.namedtuple ("Certificate", [
	"serial",
	"digest",
	"certificate",
	"private_key",
])

class CertificateAuthority:

	def __init__ (self, context, path, certificate_data):

		self.state = "none"

		self.context = context
		self.client = context.client
		self.schemas = context.schemas

		self.path = path
		self.certificate_data = certificate_data

	def create (self, name):

		if self.state != "none":
			raise Exception ()

		# sanity check

		if self.client.exists (self.path):
			raise Exception ("Already exists")

		# create key

		self.root_key = crypto.PKey ()
		self.root_key.generate_key (crypto.TYPE_RSA, 2048)

		# create certificate

		self.root_cert = crypto.X509 ()

		self.root_cert.set_pubkey (self.root_key)

		self.root_cert.set_version (2)

		self.root_cert.set_serial_number (
			struct.unpack ("Q", rand.bytes (8)) [0])

		self.root_cert.get_subject ().C = self.certificate_data ["country"]
		self.root_cert.get_subject ().L = self.certificate_data ["locality"]
		self.root_cert.get_subject ().O = self.certificate_data ["organization"]
		self.root_cert.get_subject ().CN = name

		self.root_cert.gmtime_adj_notBefore (0)
		self.root_cert.gmtime_adj_notAfter (315360000)

		self.root_cert.set_issuer (
			self.root_cert.get_subject ())

		self.root_cert.add_extensions ([

			crypto.X509Extension (
				"basicConstraints",
				True,
				"CA:TRUE, pathlen:0"),

			crypto.X509Extension (
				"keyUsage",
				True,
				"keyCertSign, cRLSign"),

			crypto.X509Extension (
				"subjectKeyIdentifier",
				False,
				"hash",
				subject = self.root_cert),

		])

		self.root_cert.add_extensions ([

			crypto.X509Extension (
				"authorityKeyIdentifier",
				False,
				"keyid,issuer:always",
				issuer = self.root_cert)

		])

		# sign certificate

		self.root_cert.sign (self.root_key, "sha256")

		# dump to pem

		self.root_cert_string = crypto.dump_certificate (
			crypto.FILETYPE_PEM,
			self.root_cert)

		self.root_key_string = crypto.dump_privatekey (
			crypto.FILETYPE_PEM,
			self.root_key)

		# write data in "creating" state

		self.data = {

			"authority_state":
				"creating",

			"subject_country":
				self.root_cert.get_subject ().C,

			"subject_locality":
				self.root_cert.get_subject ().L,

			"subject_organization":
				self.root_cert.get_subject ().O,

			"subject_common_name":
				self.root_cert.get_subject ().CN,

		}

		self.client.set_yaml (
			self.path + "/data",
			self.data,
			self.schemas ["certificate-authority"])

		# write other data

		self.client.set_raw (
			self.path + "/certificate",
			self.root_cert_string)

		self.client.set_raw (
			self.path + "/key",
			self.root_key_string)

		self.client.set_raw (
			self.path + "/serial",
			"0")

		# write data in "active" state

		self.data ["authority_state"] = "active"

		self.client.set_yaml (
			self.path + "/data",
			self.data,
			self.schemas ["certificate-authority"])

	def load (self):

		self.data = self.client.get_yaml (
			self.path + "/data")

		self.root_cert_string = self.client.get_raw (
			self.path + "/certificate")

		self.root_key_string = self.client.get_raw (
			self.path + "/key")

		root_serial_string = self.client.get_raw (
			self.path + "/serial")

		self.root_cert = crypto.load_certificate (
			crypto.FILETYPE_PEM,
			self.root_cert_string)

		self.root_key = crypto.load_privatekey (
			crypto.FILETYPE_PEM,
			self.root_key_string)

		self.issue_serial = int (root_serial_string)

	def issue (self, type, name, alt_names):

		if self.client.exists (
			self.path + "/named/" + name):

			raise Exception (
				"Certficate already exists for this common name")

		else:

			return self.reissue (type, name, alt_names)

	def reissue (self, type, name, alt_names):

		# check type

		if type == "server":

			use_server = True
			use_client = False

			use_string = "serverAuth"

		elif type == "client":

			use_server = False
			use_client = True

			use_string = "clientAuth"

		elif type == "mixed":

			use_server = True
			use_client = True

			use_string = "serverAuth, clientAuth"

		else:

			raise Exception ("Invalid type: %s" % type)

		# increase serial

		issue_serial = self.issue_serial

		issue_path = "%s/issue/%s" % (self.path, issue_serial)

		self.issue_serial += 1

		self.client.set_raw (
			self.path + "/serial",
			str (self.issue_serial))

		# create key

		issue_key = crypto.PKey ()
		issue_key.generate_key (crypto.TYPE_RSA, 2048)

		# create certificate

		issue_cert = crypto.X509 ()

		issue_cert.set_pubkey (issue_key)

		issue_cert.set_version (2)
		issue_cert.set_serial_number (issue_serial)

		issue_cert.get_subject ().C = self.certificate_data ["country"]
		issue_cert.get_subject ().L = self.certificate_data ["locality"]
		issue_cert.get_subject ().O = self.certificate_data ["organization"]
		issue_cert.get_subject ().CN = name

		issue_cert.gmtime_adj_notBefore (0)
		issue_cert.gmtime_adj_notAfter (315360000)

		issue_cert.set_issuer (self.root_cert.get_subject ())

		issue_cert.add_extensions ([

			crypto.X509Extension (
				"basicConstraints",
				False,
				"CA:FALSE"),

			crypto.X509Extension (
				"keyUsage",
				False,
				"digitalSignature, keyEncipherment"),

			crypto.X509Extension (
				"extendedKeyUsage",
				False,
				use_string),

			crypto.X509Extension (
				"subjectKeyIdentifier",
				False,
				"hash",
				subject = issue_cert),

			crypto.X509Extension (
				"authorityKeyIdentifier",
				False,
				"keyid,issuer:always",
				issuer = self.root_cert),

		])

		if (alt_names):

			issue_cert.add_extensions ([

				crypto.X509Extension (
					"subjectAltName",
					False,
					",".join (alt_names)),

			])

		# sign certificate

		issue_cert.sign (self.root_key, "sha256")

		# dump to pem

		issue_cert_string = crypto.dump_certificate (
			crypto.FILETYPE_PEM,
			issue_cert)

		issue_key_string = crypto.dump_privatekey (
			crypto.FILETYPE_PEM,
			issue_key)

		issue_digest = issue_cert.digest ("sha1")

		# write to database

		self.client.set_raw (
			issue_path + "/certificate",
			issue_cert_string)

		self.client.set_raw (
			issue_path + "/key",
			issue_key_string)

		self.client.set_raw (
			self.path + "/index/" + issue_digest,
			str (issue_serial))

		self.client.set_raw (
			self.path + "/named/" + name,
			str (issue_serial))

		return Certificate (
			serial = issue_serial,
			digest = issue_digest,
			certificate = issue_cert_string,
			private_key = issue_key_string)

	def get (self, issue_ref):

		if serial_pattern.match (issue_ref):

			pass

		elif digest_pattern.match (issue_ref):

			issue_serial = self.client.get_raw (
				"%s/index/%s" % (self.path, issue_ref))

		else:

			issue_serial = self.client.get_raw (
				"%s/named/%s" % (self.path, issue_ref))

		issue_path = "%s/issue/%s" % (
			self.path,
			issue_serial,
		)

		certificate_string = self.client.get_raw (
			issue_path + "/certificate")

		key_string = self.client.get_raw (
			issue_path + "/key")

		return Certificate (
			serial = issue_serial,
			certificate = certificate_string,
			private_key = key_string)

	def root_certificate (self):

		return self.root_cert_string

def args (prev_sub_parsers):

	parser = prev_sub_parsers.add_parser (
		"authority")

	next_sub_parsers = parser.add_subparsers ()

	args_create (next_sub_parsers)
	args_issue (next_sub_parsers)
	args_export (next_sub_parsers)

def args_create (sub_parsers):

	parser = sub_parsers.add_parser (
		"create")

	parser.set_defaults (
		func = do_create)

	parser.add_argument (
		"--authority",
		required = True)

	parser.add_argument (
		"--common-name",
		required = True)

def do_create (context, args):

	authority = CertificateAuthority (
		context,
		"/authority/" + args.authority,
		context.certificate_data)

	authority.create (args.common_name)

	print "Certificate authority created"

def args_issue (sub_parsers):

	parser = sub_parsers.add_parser (
		"issue")

	parser.set_defaults (
		func = do_issue)

	parser.add_argument (
		"--authority",
		required = True)

	parser.add_argument (
		"--common-name",
		required = True)

	# type

	parser_type = parser.add_mutually_exclusive_group (
		required = True)

	parser_type.add_argument (
		"--server",
		action = "store_const",
		const = "server",
		dest = "type")

	parser_type.add_argument (
		"--client",
		action = "store_const",
		const = "client",
		dest = "type")

	parser_type.add_argument (
		"--mixed",
		action = "store_const",
		const = "mixed",
		dest = "type")

	# store

	parser_store = parser.add_argument_group (
		"store")

	parser_store.add_argument (
		"--store-database")

	parser_store.add_argument (
		"--store-host")

	parser_store.add_argument (
		"--store-host-key")

	# alt names

	parser_alt_names = parser.add_argument_group (
		"alt names")

	parser_alt_names.add_argument (
		"--alt-dns",
		default = [],
		action = "append")

	parser_alt_names.add_argument (
		"--alt-ip",
		default = [],
		action = "append")

	parser_alt_names.add_argument (
		"--alt-email",
		default = [],
		action = "append")

def do_issue (context, args):

	authority = CertificateAuthority (
		context,
		"/authority/" + args.authority,
		context.certificate_data)

	authority.load ()

	alt_names = list (itertools.chain.from_iterable ([
		[ "DNS:" + alt_dns for alt_dns in args.alt_dns ],
		[ "IP:" + alt_ip for alt_ip in args.alt_ip ],
		[ "email:" + alt_email for alt_email in args.alt_email ],
	]))

	try:

		certificate = authority.issue (
			args.type,
			args.common_name,
			alt_names)

		print "Created certificate %s %s %s" % (
			certificate.serial,
			certificate.digest,
			args.common_name)

		if args.store_host and args.store_key:

			host_data = wbs_client.get_host (args.store_host)
			host_data [args.store_key] = issue_digest
			wbs_client.set_host (args.store_host, host_data)

			print "Stored as %s in host %s" % (
				args.store_key,
				args.store_host)

	except:

		print "Certificate already exists for %s" % (
			args.common_name)

		sys.exit (1)

def args_export (sub_parsers):

	parser = sub_parsers.add_parser ('export')
	parser.set_defaults (func = do_export)

	parser.add_argument (
		"--authority",
		required = True)

	parser.add_argument (
		"--common-name",
		required = True)

	parser.add_argument (
		"--full-certificate-chain")

	parser.add_argument (
		"--private-key")

def do_export (client, args):

	authority = CertificateAuthority (
		context.client,
		"/authority/" + args.authority,
		context.certificate_data,
		context.schemas)

	authority.load ()

	success, certificate_string, key_string = authority.get (
		args.common_name)

	if success:

		if args.full_certificate_chain:

			with open (args.full_certificate_chain, "w") as file_handle:

				file_handle.write (certificate_string)
				file_handle.write (authority.root_certificate ())

			print "Wrote full chain to %s" % (
				args.full_certificate_chain)

		if args.private_key:

			with open (args.private_key, "w") as file_handle:

				file_handle.write (key_string)

			print "Wrote private key to %s" % (
				args.private_key)

	else:

		print "failure"

def add_schemas (schemas):

	schemas.define ("certificate-authority", [

		SchemaGroup ([

			SchemaField (
				name = "authority_state",
				required = True),

			SchemaField (
				name = "authority_serial",
				required = True),

		]),

		SchemaGroup ([

			SchemaField (
				name = "subject_country",
				required = True),

			SchemaField (
				name = "subject_locality",
				required = True),

			SchemaField (
				name = "subject_organization",
				required = True),

			SchemaField (
				name = "subject_common_name",
				required = True),

		]),

	])
