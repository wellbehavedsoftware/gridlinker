from __future__ import absolute_import

from wbsdevops import command

account_command = command.CollectionCommand (

	command.CommandHelper (

		name = "amazon-account",
		command_name = "account",

		help = "manage amazon account definitions",

		custom_args = [

			command.NameArgument (
				argument = "--name",
				key = "account_name"),

			command.SimpleArgument (
				argument = "--description",
				key = "account_description",
				help = "user-friendly description"),

			command.SimpleArgument (
				argument = "--access-key-id",
				key = "access_key_id",
				help = "amazon access key id"),

			command.SimpleArgument (
				argument = "--secret-access-key",
				key = "secret_access_key",
				help = "amazon access key id"),

			command.SetArgument (),

		],

	)

)

def args (sub_parsers):

	account_command.args (sub_parsers)

# ex: noet ts=4 filetype=yaml
