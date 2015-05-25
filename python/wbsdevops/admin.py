from __future__ import absolute_import

from wbsdevops import command

admin_command = command.CollectionCommand (

	command.CommandHelper (

		name = "admin",
		help = "manage admin users",

		custom_args = [

			command.NameArgument (
				argument = "--name",
				key = "admin_name"),

			command.SimpleArgument (
				argument = "--full-name",
				key = "admin_full_name",
				value_name = "NAME",
				help = "full name of admin"),

			command.FileArgument (
				argument = "--ssh-key",
				path = "ssh-key",
				help = "public ssh key to identify admin"),

			command.SetArgument (),
			command.GeneratePasswordArgument (),

		],

	)

)

def args (sub_parsers):

	admin_command.args (sub_parsers)

# ex: noet ts=4 filetype=yaml
