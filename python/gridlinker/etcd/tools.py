from __future__ import absolute_import
from __future__ import unicode_literals

import os
import subprocess
import sys
import tempfile

from wbs import env_resolve

def args (prev_sub_parsers):

	parser = prev_sub_parsers.add_parser (
		"etcd",
		help = "tools to manage etcd directly")

	next_sub_parsers = parser.add_subparsers ()

	args_etcd_control (next_sub_parsers)
	args_etcd_edit (next_sub_parsers)
	args_etcd_export (next_sub_parsers)
	args_etcd_import (next_sub_parsers)

def args_etcd_export (sub_parsers):

	parser = sub_parsers.add_parser (
		"export",
		help = "export data from etcd")

	parser.set_defaults (
		func = do_etcd_export)

	parser.add_argument (
		"--source",
		default = "",
		help = "Etcd path to read data from")

	parser.add_argument (
		"--target",
		required = True,
		help = "Local filesystem path to write data to")

def do_etcd_export (context, args):

	tree = context.client.get_tree (args.source)

	dir_names = {}

	for key, value in tree:

		item_dir = os.path.dirname (key)

		if not item_dir in dir_names:

			print (item_dir)

			if not os.path.isdir (args.target + item_dir):
				os.makedirs (args.target + item_dir)

			dir_names [item_dir] = True

		file_handle = open (args.target + key, "w")
		file_handle.write (value)
		file_handle.close ()

def args_etcd_import (sub_parsers):

	parser = sub_parsers.add_parser (
		"import",
		help = "import data into etcd")

	parser.set_defaults (
		func = do_etcd_import)

	parser.add_argument (
		"--source",
		required = True,
		help = "Local filesyste path to read data from")

	parser.add_argument (
		"--target",
		default = "",
		help = "Etcd path to write data to")

def do_etcd_import (context, args):

	for dir_name, subdir_list, file_list in os.walk (args.source):

		dir_name = dir_name [len (args.source) + 1:]

		if len (dir_name):

			dir_name = "/" + dir_name
			print (dir_name)

		else:

			print ("/")

		for file_name in file_list:

			file_name = "/" + file_name

			with open (
				args.source + dir_name + file_name
			) as file_handle:
				file_contents = file_handle.read ()

			context.client.set_raw (
				args.target + dir_name + file_name,
				file_contents)

def args_etcd_edit (sub_parsers):

	parser = sub_parsers.add_parser (
		"edit",
		help = "edit a file in etcd")

	parser.set_defaults (
		func = do_etcd_edit)

	parser.add_argument (
		"name",
		nargs = "*")

def do_etcd_edit (context, args):

	with tempfile.NamedTemporaryFile () as temp_file:

		for name in args.name:

			file_contents = context.client.get_raw (name)

			temp_file.write (file_contents)
			temp_file.flush ()

			os.system ("%s %s" % (os.environ ["EDITOR"], temp_file.name))

			temp_file.seek (0)
			file_contents = temp_file.read ()
			temp_file.truncate ()

			context.client.set_raw (name, file_contents)

def args_etcd_control (sub_parsers):

	parser = sub_parsers.add_parser (
		"control",
		help = "invoke etcdctl directly")

	parser.set_defaults (
		func = do_etcd_control)

	parser.add_argument (
		"rest",
		nargs = "*")

def do_etcd_control (context, args):

	result = subprocess.call (
		[ "etcdctl" ] + args.rest,
		env = env_resolve (os.environ, context.env))

	sys.exit (result)

# ex: noet ts=4 filetype=yaml
