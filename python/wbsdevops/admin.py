from __future__ import absolute_import

from wbsdevops.command import CollectionCommand
from wbsdevops.command import CommandHelper

from wbsdevops.schema import SchemaGroup, SchemaField

from wbsmisc import generate_password

class AdminCommandHelper (CommandHelper):

	def __init__ (self):

		self.name = "admin"

	def get_collection (self, context):

		return context.admins

	def args_common (self, parser):

		parser.add_argument (
			"--full-name",
			help = "full name of admin")

		parser.add_argument (
			"--ssh-key",
			help = "public ssh key to identify admin")

		parser.add_argument (
			"--set",
			action = "append",
			nargs = 2,
			default = [],
			help = "miscellaneous value to store")

	def do_common (self, context, args, admin_data):

		admin_data_mappings = {
			"admin_name": "name",
			"admin_full_name": "full_name",
		}

		arg_vars = vars (args)

		for target, source in admin_data_mappings.items ():

			if not arg_vars [source]:
				continue

			admin_data [target] = arg_vars [source]

		if args.ssh_key:

			with open (args.ssh_key) as file_handle:
				ssh_key = file_handle.read ()

			context.admins.set_file (args.name, "ssh-key", ssh_key)

admin_command = CollectionCommand (
	AdminCommandHelper ())

def args (sub_parsers):

	admin_command.args (sub_parsers)

def schemas (schemas):

	schemas.define ("admin", [

		SchemaGroup ([

			SchemaField (
				name = "admin_name",
				required = True),

			SchemaField (
				name = "admin_full_name",
				required = False),

		]),

	])

# ex: noet ts=4 filetype=yaml
