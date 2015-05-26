from __future__ import absolute_import

from wbsdevops import generic

account_command = generic.GenericCommand (

	generic.CommandHelper (

		name = "amazon-vpc",
		command_name = "vpc",

		help = "manage amazon vpc definitions",

		custom_args = [

			generic.NameArgument (
				argument = "--name",
				key = "vpc_name"),

			generic.SimpleArgument (
				argument = "--description",
				key = "vpc_description",
				value_name = "DESCRIPTION",
				help = "user-friendly description"),

			generic.SimpleArgument (
				argument = "--amazon-account",
				key = "amazon_account",
				value_name = "ACCOUNT",
				help = "amazon account name"),

			generic.SimpleArgument (
				argument = "--amazon-region",
				key = "amazon_region",
				value_name = "REGION",
				help = "amazon region name"),

			generic.SimpleArgument (
				argument = "--private-network",
				key = "private_network",
				value_name = "IP",
				help = "private network ip address"),

			generic.SimpleArgument (
				argument = "--private-netmask",
				key = "private_netmask",
				value_name = "NETMASK",
				help = "private network ip netmask"),

			generic.SimpleArgument (
				argument = "--private-netmask-bits",
				key = "private_netmask_bits",
				value_name = "BITS",
				help = "private network ip netmask size in bits"),

			generic.SetArgument (),

		],

	)

)

def args (sub_parsers):

	account_command.args (sub_parsers)

# ex: noet ts=4 filetype=yaml
