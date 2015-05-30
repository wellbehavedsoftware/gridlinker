from __future__ import absolute_import
from __future__ import unicode_literals

from wbsdevops.generic import *

host_command = GenericCommand (

	CommandHelper (

		name = "host",
		help = "manage host definitions",

		custom_args = [

			ArgumentGroup (
				label = "host identity",
				arguments = [

				NameArgument (),
				GroupArgument (),

			]),
			
			ArgumentGroup (
				label = "basic host information",
				arguments = [

				SimpleArgument (
					argument = "--index",
					required = False,
					key = "host_index",
					value_name = "INDEX",
					help = "host index, eg \"1\" for \"host-1\""),

				SimpleArgument (
					argument = "--description",
					required = False,
					key = "host_description",
					value_name = "DESCRIPTION",
					help = "user-friendly description"),

			]),

			ArgumentGroup (
				label = "ansible configuration",
				arguments = [

				SimpleArgument (
					argument = "--ansible-ssh-host",
					required = False,
					key = "ansible_ssh_host",
					value_name = "HOST",
					help = "ssh hostname"),

				SimpleArgument (
					argument = "--ansible-ssh-user",
					required = False,
					key = "ansible_ssh_user",
					value_name = "USER",
					help = "ssh username"),

			]),

			ArgumentGroup (
				label = "private network configuration",
				arguments = [

				SimpleArgument (
					argument = "--private-address",
					required = False,
					key = "private_address",
					value_name = "IP",
					help = "private ip address"),

			]),

			ArgumentGroup (
				label = "amazon instance configuration",
				arguments = [
			
				AddListArgument (
					argument = "--add-amazon-balancer",
					key = "amazon_balancer_names",
					value_name = "BALANCER",
					help = "add to elastic load balancer"),
			
			]),

			ArgumentGroup (
				label = "arbitrary configuration",
				arguments = [

				MiscSetArgument (),
				MiscUnsetArgument (),

				MiscAddArgument (),
				MiscRemoveArgument (),

				GeneratePasswordArgument (),

			]),

		],

		custom_columns = [

			SimpleColumn (
				name = "host_name",
				label = "Name",
				default = True),

			SimpleColumn (
				name = "private_address",
				label = "Private IP",
				default = True),

		],

	)

)

def args (sub_parsers):

	host_command.args (sub_parsers)

# ex: noet ts=4 filetype=yaml
