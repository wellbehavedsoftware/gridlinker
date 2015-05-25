from __future__ import absolute_import

from wbsdevops import command

vpc_subnet_command = command.CollectionCommand (

	command.CommandHelper (

		name = "amazon-vpc-subnet",
		command_name = "vpc-subnet",

		help = "manage amazon vpc subnet definitions",

		custom_args = [

			command.NameArgument (
				argument = "--name",
				key = "vpc_subnet_name"),

			command.SimpleArgument (
				argument = "--description",
				key = "vpc_subnet_description",
				value_name = "DESCRIPTION",
				help = "user-friendly description"),

			command.SimpleArgument (
				argument = "--vpc-name",
				key = "vpc_name",
				value_name = "VPC",
				help = "vpc name"),

			command.SimpleArgument (
				argument = "--amazon-zone",
				key = "amazon_zone",
				value_name = "ZONE",
				help = "amazon zone name"),

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

	vpc_subnet_command.args (sub_parsers)

# ex: noet ts=4 filetype=yaml
