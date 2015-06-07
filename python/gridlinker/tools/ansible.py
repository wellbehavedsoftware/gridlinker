from __future__ import absolute_import
from __future__ import unicode_literals

import os
import subprocess
import sys

import gridlinker

from wbs import env_resolve

def args (prev_sub_parsers):

	parser = prev_sub_parsers.add_parser (
		"ansible",
		help = "manage or invoke ansible",
		description = """
			The ansible command group contains various commands which can be
			used to hook into ansible directly. Using this tool instead of using
			the ansible binaries directly ensures that the environment is set up
			correctly.
		""")

	next_sub_parsers = parser.add_subparsers ()

	args_playbook (next_sub_parsers)
	args_inventory (next_sub_parsers)

def args_playbook (sub_parsers):

	parser = sub_parsers.add_parser (
		"playbook",
		help = "run an ansible playbook",
		description = """
			This command will execute ansible-playbook directly, passing along
			any arguments unchanged. Remember that you will normally want to
			place a double-dash "--" between the playbook command and the
			arguments which are to be passed to ansible.
		""")

	parser.set_defaults (
		func = do_playbook)

	parser.add_argument (
		"rest",
		nargs = "*",
		help = "arguments to be passed verbatim to ansible-playbook")

def do_playbook (context, args):

	run_playbook (context, args.rest, "exit")

def run_playbook (context, args, action):

	context.ansible_init ()

	with open ("work/ansible.cfg", "w") as file_handle:

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

	if action == "ignore":

		return

	elif action == "boolean":

		return result == 0

	elif action == "integer":

		return result

	elif action == "exit":

		if result != 0:
			sys.exit (result)

	elif action == "error":

		if result != 0:
			raise Exception (
				"Ansible exited with status %s" % result)

	else:

		raise Exception (
			"Invalid result option: %s" % action)

def args_inventory (sub_parsers):

	parser = sub_parsers.add_parser (
		"inventory",
		help = "run the ansible inventory script",
		description = """
			This command will execute the inventory-script, along with the
			appropriate environment which it needs to work correctly. This is
			useful for debugging.
		""")

	parser.set_defaults (
		func = do_inventory)

	parser.add_argument (
		"rest",
		nargs = "*",
		help = "arguments to be passed verbatim to inventory-script")

def do_inventory (context, args):

	gridlinker.generic.inventory.main (context, args.rest)

# ex: noet ts=4 filetype=yaml
