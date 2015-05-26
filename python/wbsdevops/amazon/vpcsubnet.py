from __future__ import absolute_import

from wbsdevops import generic

vpc_subnet_command = generic.GenericCommand (

	generic.CommandHelper (

		name = "amazon-vpc-subnet",
		command_name = "vpc-subnet",

		help = "manage amazon vpc subnet definitions",

		custom_args = [

			generic.NameArgument (
				argument = "--name",
				key = "vpc_subnet_name"),

			generic.SimpleArgument (
				argument = "--description",
				key = "vpc_subnet_description",
				value_name = "DESCRIPTION",
				help = "user-friendly description"),

			generic.SimpleArgument (
				argument = "--vpc-name",
				key = "vpc_name",
				value_name = "VPC",
				help = "vpc name"),

			generic.SimpleArgument (
				argument = "--amazon-zone",
				key = "amazon_zone",
				value_name = "ZONE",
				help = "amazon zone name"),

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

	vpc_subnet_command.args (sub_parsers)

# ex: noet ts=4 filetype=yaml
