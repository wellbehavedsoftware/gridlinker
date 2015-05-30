from __future__ import absolute_import
from __future__ import unicode_literals

from wbsdevops.generic import *

group_command = GenericCommand (

	CommandHelper (

		name = "group",
		help = "manage group definitions",

		custom_args = [

			ArgumentGroup (
				label = "group identity",
				arguments = [

				NameArgument (),
				ClassArgument (),
				ParentArgument (),

			]),

			ArgumentGroup (
				label = "basic group information",
				arguments = [

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
				MiscUnsetArgument (),

				MiscAddArgument (),
				MiscRemoveArgument (),

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
