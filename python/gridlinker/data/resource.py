from __future__ import absolute_import
from __future__ import unicode_literals

from gridlinker.tools import *

class ResourceHelper (CommandHelper):

	def get_unique_name (self, context, args):

		arg_vars = vars (args)

		# verify group or class

		if "group" in arg_vars and arg_vars ["group"]:

			if getattr (args, "class"):
				raise Exception ()

			group_name = args.group
			group_data = context.groups.get_quick (group_name)

			class_name = group_data ["identity"] ["class"]
			class_data = context.local_data ["classes"] [class_name]

		elif "class" in arg_vars \
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

		if class_data ["class"] ["scope"] == "group":
			unique_name = "%s/%s" % (group_name, args.name)

		elif class_data ["class"] ["scope"] == "class":
			unique_name = "%s/%s" % (class_name, args.name)

		elif class_data ["class"] ["scope"] == "global":
			unique_name = args.name

		else:
			raise Exception ()

		return unique_name

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
				GroupArgument (),
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

			SimpleColumn (
				section = "identity",
				name = "name",
				label = "Name",
				default = True),

			SimpleColumn (
				section = "identity",
				name = "group",
				label = "Group",
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
