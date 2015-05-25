from __future__ import absolute_import

from wbsdevops import command

account_command = command.CollectionCommand (

	command.CommandHelper (

		name = "amazon-vpc",
		command_name = "vpc",

		help = "manage amazon vpc definitions",

		custom_args = [

			command.NameArgument (
				argument = "--name",
				key = "vpc_name"),

			command.SimpleArgument (
				argument = "--description",
				key = "vpc_description",
				value_name = "DESCRIPTION",
				help = "user-friendly description"),

			command.SimpleArgument (
				argument = "--amazon-account",
				key = "amazon_account",
				value_name = "ACCOUNT",
				help = "amazon account name"),

			command.SimpleArgument (
				argument = "--amazon-region",
				key = "amazon_region",
				value_name = "REGION",
				help = "amazon region name"),

			command.SimpleArgument (
				argument = "--private-network",
				key = "private_network",
				value_name = "IP",
				help = "private network ip address"),

			command.SimpleArgument (
				argument = "--private-netmask",
				key = "private_netmask",
				value_name = "NETMASK",
				help = "private network ip netmask"),

			command.SimpleArgument (
				argument = "--private-netmask-bits",
				key = "private_netmask_bits",
				value_name = "BITS",
				help = "private network ip netmask size in bits"),

			command.SetArgument (),

		],

	)

)

def args (sub_parsers):

	account_command.args (sub_parsers)

# ex: noet ts=4 filetype=yaml
