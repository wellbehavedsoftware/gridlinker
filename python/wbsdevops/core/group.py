from __future__ import absolute_import

from wbsdevops.generic import *

group_command = GenericCommand (

	CommandHelper (

		name = "group",
		help = "manage group definitions",

		custom_args = [

			ArgumentGroup (
				label = "basic group information",
				arguments = [

				NameArgument (),

				SimpleArgument (
					argument = "--class",
					required = True,
					key = "group_class",
					value_name = "CLASS",
					help = "class this group belongs to"),

				SimpleArgument (
					argument = "--parent",
					required = False,
					key = "group_parent",
					value_name = "PARENT",
					help = "parent group of this group"),

				SimpleArgument (
					argument = "--description",
					required = False,
					key = "group_description",
					value_name = "DESCRIPTION",
					help = "user-friendly description"),

			]),

			ArgumentGroup (
				label = "arbitrary configuration",
				arguments = [

				MiscSetArgument (),
				MiscAddArgument (),
				GeneratePasswordArgument (),

			]),

		],

		custom_columns = [

			SimpleColumn (
				name = "group_name",
				label = "Name",
				default = True),

			SimpleColumn (
				name = "group_class",
				label = "Class",
				default = True),

			SimpleColumn (
				name = "group_parent",
				label = "Parent",
				default = True),

			SimpleColumn (
				name = "group_description",
				label = "Description",
				default = True),

		],

	)

)

def args (sub_parsers):

	group_command.args (sub_parsers)

# ex: noet ts=4 filetype=yaml
