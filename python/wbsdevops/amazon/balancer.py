from __future__ import absolute_import

from wbsdevops.generic import *

balancer_command = GenericCommand (

	CommandHelper (

		name = "amazon-balancer",
		command_name = "balancer",

		help = "manage amazon elastic load balancer definitions",

		custom_args = [

			ArgumentGroup (
				label = "basic balancer information",
				arguments = [

				NameArgument (
					argument = "--name",
					key = "balancer_name"),

				SimpleArgument (
					argument = "--description",
					key = "balancer_description",
					value_name = "DESCRIPTION",
					help = "user-friendly description"),

			]),

			ArgumentGroup (
				label = "amazon placement",
				arguments = [

				SimpleArgument (
					argument = "--amazon-account",
					key = "amazon_account_name",
					value_name = "ACCOUNT",
					help = "amazon account name"),

				SimpleArgument (
					argument = "--amazon-region",
					key = "amazon_region_name",
					value_name = "REGION",
					help = "amazon region name"),

				SimpleArgument (
					argument = "--vpc",
					key = "amazon_vpc_name",
					help = "name of vpc",
					value_name = "SUBNET"),

				AddListArgument (
					argument = "--add-vpc-subnet",
					key = "amazon_vpc_subnet_names",
					help = "add a vpc subnet region",
					value_name = "SUBNET"),

			]),

			ArgumentGroup (
				label = "arbitrary configuration",
				arguments = [

				SetArgument (),

			]),

		],

		custom_columns = [

			SimpleColumn (
				name = "balancer_name",
				label = "Name",
				default = True),

			SimpleColumn (
				name = "balancer_description",
				label = "Description",
				default = True),

		],

	)

)

def args (sub_parsers):

	balancer_command.args (sub_parsers)

# ex: noet ts=4 filetype=yaml
