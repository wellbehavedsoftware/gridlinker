from __future__ import absolute_import
from __future__ import unicode_literals

from gridlinker.tools import *

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
				section = "identity",
				name = "name",
				label = "Name",
				default = True),

			SimpleColumn (
				section = "identity",
				name = "class",
				label = "Class",
				default = True),

			SimpleColumn (
				section = "identity",
				name = "parent",
				label = "Parent",
				default = True),

			SimpleColumn (
				section = "identity",
				name = "description",
				label = "Description",
				default = True),

		],

	)

)

def args (sub_parsers):

	group_command.args (sub_parsers)

# ex: noet ts=4 filetype=yaml
