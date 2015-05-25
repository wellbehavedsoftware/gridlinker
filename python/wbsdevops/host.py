from __future__ import absolute_import

import os
import paramiko.ecdsakey
import paramiko.rsakey
import tempfile

import StringIO

from wbsdevops import yamlx

from wbsmisc import generate_password

def args (prev_sub_parser):

	parser = prev_sub_parser.add_parser ("host")
	next_sub_parsers = parser.add_subparsers ()

	args_get (next_sub_parsers)
	args_set (next_sub_parsers)
	args_unset (next_sub_parsers)
	args_edit (next_sub_parsers)
	args_create (next_sub_parsers)
	args_show (next_sub_parsers)

def args_get (sub_parsers):

	parser = sub_parsers.add_parser (
		"get")

	parser.set_defaults (
		func = do_get)

	parser.add_argument (
		"host",
		help = "Host to read data from")

	parser.add_argument (
		"key",
		help = "Key to read from host")

def do_get (context, args):

	host_data = context.hosts.get (args.host)

	print host_data [args.key]

	pass

def args_set (sub_parsers):

	parser = sub_parsers.add_parser (
		"set")

	parser.set_defaults (
		func = do_set)

	parser.add_argument (
		"host",
		help = "Host to set data in")

	parser.add_argument (
		"key",
		help = "Key to set in host")

	parser.add_argument (
		"value",
		help = "Value to set in host")

def do_set (context, args):

	host_data = context.hosts.get (args.host)

	host_data [key] = value

	context.hosts.set (args.host, host_data)

def args_unset (sub_parsers):

	parser = sub_parsers.add_parser (
		"unset")

	parser.set_defaults (
		func = do_unset)

	parser.add_argument (
		"host",
		help = "Host to remove data from")

	parser.add_argument (
		"key",
		help = "Key to remove from host")

def do_unset (context, args):

	host_data = context.hosts.get (args.host)

	del host_data [key]

	context.hosts.set (
		args.host,
		host_data)

def args_edit (sub_parsers):

	parser = sub_parsers.add_parser (
		"edit")

	parser.set_defaults (
		func = do_edit)

	parser.add_argument (
		"host",
		help = "Host to edit")

def do_edit (context, args):

	if not context.hosts.exists (args.host):

		raise Exception (
			"Host does not exist: " + args.host)

	host_data = context.hosts.get (args.host)

	temp_file = tempfile.NamedTemporaryFile ()

	host_yaml = yamlx.encode (
		context.schemas ["host"],
		host_data)

	temp_file.write (host_yaml)
	temp_file.flush ()

	os.system ("%s %s" % (os.environ ["EDITOR"], temp_file.name))

	temp_again = open (temp_file.name, "r")
	host_yaml = temp_again.read ()

	host_data = yamlx.parse (
		host_yaml)

	temp_again.close ()

	context.hosts.set (
		"/host/" + args.host,
		host_data)

def args_create (sub_parsers):

	parser = sub_parsers.add_parser (
		"create")

	parser.set_defaults (
		func = do_create)

	parser.add_argument (
		"--edit",
		action = "store_true",
		help = "edit host data before creating")

	group = parser.add_argument_group (
		"basic host information")

	group.add_argument (
		"--host-name",
		required = True,
		help = "name of host to create")

	group.add_argument (
		"--host-group",
		action = "append",
		dest = "host_groups",
		default = [],
		help = "group to add host to, can use multiple times")

	group.add_argument (
		"--host-index",
		help = "host index, eg \"1\" for \"host-1\"")

	group = parser.add_argument_group (
		title = "ansbile configuration")

	group.add_argument (
		"--ansible-ssh-host",
		help = "ssh hostname")

	group.add_argument (
		"--ansible-ssh-user",
		help = "ssh user")

	group = parser.add_argument_group (
		title = "private network configuration")

	group.add_argument (
		"--private-address",
		help = "ip address")

	group = parser.add_argument_group (
		title = "arbitrary configuration")

	group.add_argument (
		"--generate-password",
		action = "append",
		default = [],
		help = "generate random password to store")

def do_create (context, args):

	if context.hosts.exists (args.host_name):

		raise Exception (
			"Host already exists: " + args.host_name)

	arg_names = [
		"host_name",
		"host_groups",
		"host_index",
		"ansible_ssh_host",
		"ansible_ssh_user",
		"private_address",
	]

	host_data = {}

	arg_vars = vars (args)

	for arg_name in arg_names:

		if not arg_vars [arg_name]:
			continue

		host_data [arg_name] = arg_vars [arg_name]

	for key in args.generate_password:

		host_data [key] = generate_password ()

	if args.edit:

		temp_file = tempfile.NamedTemporaryFile ()

		host_yaml = yamlx.encode (
			context.schemas ["host"],
			host_data)

		temp_file.write (host_yaml)
		temp_file.flush ()

		os.system ("%s %s" % (os.environ ["EDITOR"], temp_file.name))

		temp_again = open (temp_file.name, "r")
		host_yaml = temp_again.read ()

		host_data = yamlx.parse (
			host_yaml)

		temp_again.close ()

	context.hosts.set (args.host_name, host_data)

	host_ssh_keys = {
		"ecdsa": paramiko.ecdsakey.ECDSAKey.generate (),
		"rsa": paramiko.rsakey.RSAKey.generate (2048),
	}

	for host_key_type, host_key in host_ssh_keys.items ():

		host_key_public = " ".join ([
			host_key.get_name (),
			host_key.get_base64 (),
			args.host_name,
		])

		host_key_private_io = StringIO.StringIO ()
		host_key.write_private_key (host_key_private_io)
		host_key_private = host_key_private_io.getvalue ()

		context.hosts.set_file (
			args.host_name,
			"ssh-host-key/%s/public" % host_key_type,
			host_key_public)

		context.hosts.set_file (
			args.host_name,
			"ssh-host-key/%s/private" % host_key_type,
			host_key_private)

	print "Created host %s" % args.host_name

def schemas (schemas):

	pass

def args_show (sub_parsers):

	parser = sub_parsers.add_parser (
		"show")

	parser.set_defaults (
		func = do_show)

	parser.add_argument (
		"host",
		help = "Host to show")

def do_show (context, args):

	host_data = context.hosts.get (args.host)

	host_yaml = context.hosts.to_yaml (host_data)

	print host_yaml

def schemas (schemas):

	pass

# ex: noet ts=4 filetype=yaml
