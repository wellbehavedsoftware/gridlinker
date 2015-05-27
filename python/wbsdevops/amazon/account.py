from __future__ import absolute_import

from wbsdevops.generic import *

account_command = GenericCommand (

	CommandHelper (

		name = "amazon-account",
		command_name = "account",

		help = "manage amazon account definitions",

		custom_args = [

			NameArgument (
				argument = "--name",
				key = "account_name"),

			SimpleArgument (
				argument = "--description",
				key = "account_description",
				value_name = "DESCRIPTION",
				help = "user-friendly description"),

			SimpleArgument (
				argument = "--access-key-id",
				key = "access_key_id",
				value_name = "ID",
				help = "amazon access key id"),

			SimpleArgument (
				argument = "--secret-access-key",
				key = "secret_access_key",
				value_name = "KEY",
				help = "amazon access key id"),

			AddDictionaryArgument (
				argument = "--add-ssh-key",
				key = "ssh_keys",
				help = "add an ssh key",
				key_name = "NAME",
				value_name = "SOURCE"),

			AddListArgument (
				argument = "--add-region",
				key = "amazon_regions",
				help = "add an amazon region",
				value_name = "REGION"),

			MiscSetArgument (),

		],

		custom_columns = [

			SimpleColumn (
				name = "account_name",
				label = "Name",
				default = True),

			SimpleColumn (
				name = "account_description",
				label = "Description",
				default = True),

		],

	)

)

def args (sub_parsers):

	account_command.args (sub_parsers)

# ex: noet ts=4 filetype=yaml
