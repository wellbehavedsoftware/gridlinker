from __future__ import absolute_import

import etcd
import os

def args (prev_sub_parser):

	parser = prev_sub_parser.add_parser ("etcd")
	next_sub_parsers = parser.add_subparsers ()

	args_export (next_sub_parsers)
	args_import (next_sub_parsers)

def args_export (sub_parsers):

	parser = sub_parsers.add_parser (
		"export")

	parser.set_defaults (
		func = do_export)

	parser.add_argument (
		"--source",
		default = "",
		help = "Etcd path to read data from")

	parser.add_argument (
		"--target",
		required = True,
		help = "Local filesystem path to write data to")

def do_export (context, args):

	print "TODO"

def args_import (sub_parsers):

	parser = sub_parsers.add_parser (
		"import")

	parser.set_defaults (
		func = do_import)

	parser.add_argument (
		"--source",
		required = True,
		help = "Local filesyste path to read data from")

	parser.add_argument (
		"--target",
		default = "",
		help = "Etcd path to write data to")

def do_import (context, args):

	for dir_name, subdir_list, file_list in os.walk (args.source):

		dir_name = dir_name [len (args.source) + 1:]

		print "/" + dir_name

		for file_name in file_list:

			with open (
				args.source + "/" + dir_name + "/" + file_name
			) as file_handle:
				file_contents = file_handle.read ()

			context.client.etcd_client.write (
				args.target + "/" + dir_name + "/" + file_name,
				file_contents)

# ex: noet ts=4 filetype=yaml
