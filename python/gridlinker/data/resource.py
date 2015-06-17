from __future__ import absolute_import
from __future__ import unicode_literals

from gridlinker.tools import *

class ResourceHelper (CommandHelper):

	def create_unique_name (self, context, args):

		arg_vars = vars (args)

		# verify class

		if "class" in arg_vars \
		and arg_vars ["class"]:

			class_name = arg_vars ["class"]

			if not class_name in context.classes:

				raise Exception (
					"No such class: %s" % (
						class_name))

			class_data = context.local_data ["classes"] [class_name]

		else:

			resource_data = context.resources.get_slow (args.name)

			class_name = resource_data ["identity"] ["class"]
			class_data = context.local_data ["classes"] [class_name]

		# determine unique name depending on scope

		if "/" in args.name:
			unique_name = args.name

		elif class_data ["class"] ["scope"] == "class":
			unique_name = "%s/%s" % (class_name, args.name)

		elif class_data ["class"] ["scope"] == "global":
			unique_name = args.name

		else:
			raise Exception ()

		return unique_name

	def existing_unique_name (self, context, resource_data):

		resource_name = resource_data ["identity"] ["name"]

		class_name = resource_data ["identity"] ["class"]
		class_data = context.local_data ["classes"] [class_name]

		# determine unique name depending on scope

		if class_data ["class"] ["scope"] == "class":
			return "%s/%s" % (class_name, resource_name)

		elif class_data ["class"] ["scope"] == "global":
			return resource_name

		else:
			raise Exception ()

resource_command = GenericCommand (

	ResourceHelper (

		name = "resource",
		help = "manage resource definitions",

		custom_args = [

			ArgumentGroup (
				label = "resource identity",
				arguments = [

				NameArgument (),
				ClassArgument (),
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
