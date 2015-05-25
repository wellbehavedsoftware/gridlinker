from __future__ import absolute_import

from wbsdevops import command

host_command = command.CollectionCommand (

	command.CommandHelper (

		name = "host",
		help = "manage host definitions",

		custom_args = [

			command.ArgumentGroup (
				label = "basic host information",
				arguments = [

				command.NameArgument (
					argument = "--name",
					key = "host_name"),

				command.SimpleArgument (
					argument = "--description",
					key = "host_description",
					value_name = "DESCRIPTION",
					help = "user-friendly description"),

				command.AddListArgument (
					argument = "--host-group",
					key = "host_group",
					value_name = "GROUP",
					help = "group to add host to"),

				command.SimpleArgument (
					argument = "--host-index",
					key = "host_index",
					value_name = "INDEX",
					help = "host index, eg \"1\" for \"host-1\""),

			]),

			command.ArgumentGroup (
				label = "ansible configuration",
				arguments = [

				command.SimpleArgument (
					argument = "--ansible-ssh-host",
					key = "ansible_ssh_host",
					value_name = "HOST",
					help = "ssh hostname"),

				command.SimpleArgument (
					argument = "--ansible-ssh-user",
					key = "ansible_ssh_user",
					value_name = "USER",
					help = "ssh username"),

			]),

			command.ArgumentGroup (
				label = "private network configuration",
				arguments = [

				command.SimpleArgument (
					argument = "--private-address",
					key = "private_address",
					value_name = "IP",
					help = "private ip address"),

			]),

			command.ArgumentGroup (
				label = "arbitrary configuration",
				arguments = [

				command.SetArgument (),
				command.GeneratePasswordArgument (),

			]),

		],

	)

)

def args (sub_parsers):

	host_command.args (sub_parsers)

# ex: noet ts=4 filetype=yaml
