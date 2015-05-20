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

	etcd_root = context.client.etcd_client.read (args.source, recursive = True)

	dir_names = {}

	for etcd_item in etcd_root.children:

		relative_key = etcd_item.key [len (args.source):]

		print relative_key

		item_dir = os.path.dirname (relative_key)

		if not item_dir in dir_names:

			print item_dir

			if not os.path.isdir (args.target + item_dir):
				os.makedirs (args.target + item_dir)

			dir_names [item_dir] = True

		file_handle = open (args.target + relative_key, "w")
		file_handle.write (etcd_item.value)
		file_handle.close ()

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

			context.client.set_raw (
				args.target + "/" + dir_name + "/" + file_name,
				file_contents)

# ex: noet ts=4 filetype=yaml
