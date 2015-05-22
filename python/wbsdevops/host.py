from __future__ import absolute_import

import os
import tempfile

from wbsdevops import yamlx

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

	host_data = context.client.get_yaml (args.host)

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

	host_data = context.client.get_yaml (args.host)

	host_data [key] = value

	context.client.set_yaml (args.host, host_data, context.schemas ["host"])

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

	host_data = context.client.get_yaml (args.host)

	del host_data [key]

	context.client.set_yaml (args.host, host_data, context.schemas ["host"])

def args_edit (sub_parsers):

	parser = sub_parsers.add_parser (
		"edit")

	parser.set_defaults (
		func = do_edit)

	parser.add_argument (
		"host",
		help = "Host to edit")

def do_edit (context, args):

	if not context.client.exists (
			"/host/" + args.host):

		raise Exception (
			"Host does not exist: " + args.host)

	host_data = context.client.get_yaml (
		"/host/" + args.host)

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

	context.client.set_yaml (
		"/host/" + args.host,
		host_data,
		context.schemas ["host"])

def args_create (sub_parsers):

	parser = sub_parsers.add_parser (
		"create")

	parser.set_defaults (
		func = do_create)

	parser.add_argument (
		"host",
		help = "Host to create")

def do_create (context, args):

	if context.client.exists (
			"/host/" + args.host):

		raise Exception (
			"Host already exists: " + args.host)

	host_data = {
		"host_name": args.host,
	}

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

	context.client.set_yaml (
		"/host/" + args.host,
		host_data,
		context.schemas ["host"])

def args_show (sub_parsers):

	parser = sub_parsers.add_parser (
		"show")

	parser.set_defaults (
		func = do_show)

	parser.add_argument (
		"host",
		help = "Host to show")

def do_show (context, args):

	host_data = context.client.get_yaml (args.host)

	host_yaml = context.client.host_to_yaml (host_data)
	print host_yaml

	pass
