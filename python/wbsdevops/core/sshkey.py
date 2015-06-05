from __future__ import absolute_import
from __future__ import unicode_literals

import io
import os
import paramiko.rsakey
import StringIO
import tempfile

def args (prev_sub_parser):

	parser = prev_sub_parser.add_parser ("ssh-key")
	next_sub_parsers = parser.add_subparsers ()

	args_generate (next_sub_parsers)

def args_generate (sub_parsers):

	parser = sub_parsers.add_parser (
		"generate")

	parser.set_defaults (
		func = do_generate)

	parser.add_argument (
		"--name",
		required = True,
		help = "name of ssh key to generate")

	parser.add_argument (
		"--comment",
		help = "comment to append to public key")

def do_generate (context, args):

	key_path = "/ssh-key/%s" % args.name

	if context.client.exists (key_path):

		raise Exception ()

	key = paramiko.rsakey.RSAKey.generate (2048)

	public_key = " ".join ([
		key.get_name (),
		key.get_base64 (),
		args.comment or args.name,
	])

	private_key_io = StringIO.StringIO ()
	key.write_private_key (private_key_io)
	private_key = private_key_io.getvalue ()

	context.client.set_raw (
		"%s/public" % key_path,
		public_key)

	context.client.set_raw (
		"%s/private" % key_path,
		private_key)

	print ("Generated ssh key %s" % args.name)

# ex: noet ts=4 filetype=yaml
