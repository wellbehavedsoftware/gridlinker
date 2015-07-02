from __future__ import absolute_import
from __future__ import unicode_literals

from gridlinker.tools import *

class ResourceHelper (CommandHelper):

	def create_unique_name (self, context, args):

		arg_vars = vars (args)

		# verify class

		class_name = arg_vars ["class"]

		if not class_name in context.classes:

			raise Exception (
				"No such class: %s" % (
					class_name))

		class_data = context.local_data ["classes"] [class_name]

		return "%s/%s" % (
			class_data ["class"] ["namespace"],
			args.name)

	def existing_unique_name (self, context, resource_data):

		resource_name = resource_data ["identity"] ["name"]

		class_name = resource_data ["identity"] ["class"]
		class_data = context.local_data ["classes"] [class_name]

		# determine unique name depending on scope

		return "%s/%s" % (
			class_data ["class"] ["namespace"],
			resource_data ["identity"] ["name"])

resource_command = GenericCommand (

	ResourceHelper (

		name = "resource",
		help = "manage resource definitions",

		custom_args = [

			ArgumentGroup (
				label = "resource identity",
				arguments = [

				ClassArgument (),
				NameArgument (),
				ParentArgument (),
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

				MiscSetFileArgument (),

				GeneratePasswordArgument (),

			]),

		],

		custom_columns = [

			UniqueNameColumn (),

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

	resource_command.args (sub_parsers)

# ex: noet ts=4 filetype=yaml
