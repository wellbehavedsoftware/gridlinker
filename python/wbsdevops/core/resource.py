from __future__ import absolute_import
from __future__ import unicode_literals

from wbsdevops.generic import *

resource_command = GenericCommand (

	CommandHelper (

		name = "resource",
		help = "manage resource definitions",

		custom_args = [

			ArgumentGroup (
				label = "resource identity",
				arguments = [

				NameArgument (),
				ClassArgument (),
				GroupArgument (),
				IndexArgument (),

			]),
			
			ArgumentGroup (
				label = "arbitrary configuration",
				arguments = [

				MiscSetArgument (),
				MiscUnsetArgument (),

				MiscAddArgument (),
				MiscRemoveArgument (),

				MiscSetDictArgument (),
				MiscUnsetDictArgument (),

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
				section = "private",
				name = "address",
				label = "Private IP",
				default = True),

		],

	)

)

def args (sub_parsers):

	resource_command.args (sub_parsers)

# ex: noet ts=4 filetype=yaml
