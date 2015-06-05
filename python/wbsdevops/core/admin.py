from __future__ import absolute_import
from __future__ import unicode_literals

from wbsdevops.generic import *

admin_command = GenericCommand (

	CommandHelper (

		name = "admin",
		help = "manage admin users",
		description = """
			This command allows you to manage a simple database of admin users,
			along with their access credentials and other basic information.
		""",

		custom_args = [

			ArgumentGroup (
				label = "basic admin information",
				arguments = [

				NameArgument (),

				SimpleArgument (
					argument = "--full-name",
					required = False,
					key = "admin_full_name",
					value_name = "NAME",
					help = "full name of admin"),

				FileArgument (
					argument = "--ssh-key",
					path = "ssh-key",
					help = "public ssh key to identify admin"),

			]),

			ArgumentGroup (
				label = "arbitrary configuration",
				arguments = [

				MiscSetArgument (),
				#MiscAddArgument (),
				#GeneratePasswordArgument (),

			]),

		],

		custom_columns = [

			SimpleColumn (
				section = "identity",
				name = "name",
				label = "Name",
				default = True),

			SimpleColumn (
				section = "identity",
				name = "full_name",
				label = "Full name",
				default = True),

		],

	)

)

def args (sub_parsers):

	admin_command.args (sub_parsers)

# ex: noet ts=4 filetype=yaml
