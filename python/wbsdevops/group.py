from __future__ import absolute_import

from wbsdevops import yamlx
from wbsdevops.schema import SchemaGroup, SchemaField
from wbsdevops.command import CollectionCommand
from wbsdevops.command import CommandHelper

from wbsmisc import generate_password

class GroupCommandHelper (CommandHelper):

	def __init__ (self):

		self.name = "group"

	def get_collection (self, context):

		return context.groups

	def args_common (self, parser):

		parser.add_argument (
			"--description",
			help = "user-friendly description")

		parser.add_argument (
			"--set",
			action = "append",
			nargs = 2,
			default = [],
			help = "miscellaneous value to store")

		parser.add_argument (
			"--generate-password",
			action = "append",
			default = [],
			help = "generate random password to store")

	def do_common (self, context, args, group_data):

		group_data_mappings = {
			"group_name": "name",
			"group_description": "description",
		}

		arg_vars = vars (args)

		for target, source in group_data_mappings.items ():

			if not arg_vars [source]:
				continue

			group_data [target] = arg_vars [source]

		for key, value in args.set:

			group_data [key] = value

		for key in args.generate_password:

			group_data [key] = generate_password ()

group_command = CollectionCommand (
	GroupCommandHelper ())

def args (sub_parsers):

	group_command.args (sub_parsers)

def schemas (schemas):

	schemas.define ("group", [

		SchemaGroup ([

			SchemaField (
				name = "group_name",
				required = True),

			SchemaField (
				name = "group_description",
				required = False),

		]),

	])

# ex: noet ts=4 filetype=yaml
