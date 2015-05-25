from __future__ import absolute_import

from wbsdevops import command

group_command = command.CollectionCommand (

	command.CommandHelper (

		name = "group",
		help = "manage group definitions",

		custom_args = [

			command.NameArgument (
				argument = "--name",
				key = "group_name"),

			command.SimpleArgument (
				argument = "--description",
				key = "group_description",
				help = "user-friendly description"),

			command.SetArgument (),
			command.GeneratePasswordArgument (),

		],

	)

)

def args (sub_parsers):

	group_command.args (sub_parsers)

# ex: noet ts=4 filetype=yaml
