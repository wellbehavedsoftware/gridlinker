from __future__ import absolute_import

import os
import subprocess
import sys

from wbsmisc import env_resolve

def args (prev_sub_parsers):

	parser = prev_sub_parsers.add_parser (
		"ansible")

	next_sub_parsers = parser.add_subparsers ()

	args_playbook (next_sub_parsers)

def args_playbook (sub_parsers):

	parser = sub_parsers.add_parser (
		"playbook")

	parser.set_defaults (
		func = do_playbook)

	parser.add_argument (
		"rest",
		nargs = "*")

def do_playbook (context, args):

	run_playbook (context, args.rest)

def run_playbook (context, args):

	context.ansible_init ()

	with file ("work/ansible.cfg", "w") as file_handle:

		for index, (section_name, section_data) \
		in enumerate (context.ansible_config.items ()):

			if index > 0:
				file_handle.write ("\n")

			file_handle.write ("[%s]\n" % section_name)

			for key, value in section_data.items ():
				file_handle.write ("%s = %s\n" % (key, value))

	result = subprocess.call (
		[
			"%s/bin/ansible-playbook" % context.ansible_home,
		] + context.ansible_args + args,
		env = env_resolve (os.environ, context.env))

	sys.exit (result)
