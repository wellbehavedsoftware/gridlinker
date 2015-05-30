from __future__ import absolute_import

from wbsdevops.generic import *

account_command = GenericCommand (

	CommandHelper (

		name = "amazon-vpc",
		short_name = "vpc",
		command_name = "vpc",

		help = "manage amazon vpc definitions",

		custom_args = [

			ArgumentGroup (
				label = "basic vpc information",
				arguments = [

				NameArgument (),
				GroupArgument (),

				SimpleArgument (
					argument = "--description",
					required = False,
					key = "vpc_description",
					value_name = "DESCRIPTION",
					help = "user-friendly description"),

			]),

			ArgumentGroup (
				label = "amazon placement",
				arguments = [

				SimpleArgument (
					argument = "--amazon-account",
					required = False,
					key = "amazon_account_name",
					value_name = "ACCOUNT",
					help = "amazon account name"),

				SimpleArgument (
					argument = "--amazon-region",
					required = False,
					key = "amazon_region_name",
					value_name = "REGION",
					help = "amazon region name"),

			]),

			ArgumentGroup (
				label = "private network configuration",
				arguments = [

				SimpleArgument (
					argument = "--private-network",
					required = False,
					key = "private_network_name",
					value_name = "IP",
					help = "private network ip address"),

				SimpleArgument (
					argument = "--private-netmask",
					required = False,
					key = "private_netmask",
					value_name = "NETMASK",
					help = "private network ip netmask"),

				SimpleArgument (
					argument = "--private-netmask-bits",
					required = False,
					key = "private_netmask_bits",
					value_name = "BITS",
					help = "private network ip netmask size in bits"),

			]),

			ArgumentGroup (
				label = "arbitrary configuration",
				arguments = [

				MiscSetArgument (),

			]),

		],

		custom_columns = [

			SimpleColumn (
				name = "vpc_name",
				label = "Name",
				default = True),

			SimpleColumn (
				name = "vpc_description",
				label = "Description",
				default = True),

		],

	)

)

def args (sub_parsers):

	account_command.args (sub_parsers)

# ex: noet ts=4 filetype=yaml
