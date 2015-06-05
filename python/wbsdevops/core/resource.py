from __future__ import absolute_import
from __future__ import unicode_literals

from wbsdevops.generic import *

class ResourceHelper (CommandHelper):

	def get_unique_name (self, context, args):

		# verify group or class

		if args.group:

			if getattr (args, "class") and args.group:
				raise Exception ()

			group_name = args.group
			group_data = context.groups.get (group_name)

			class_name = group_data ["identity"] ["class"]
			class_data = context.local_data ["classes"] [class_name]

		elif getattr (args, "class"):

			class_name = getattr (args, "class")
			class_data = context.local_data ["classes"] [class_name]

		else:
			raise Exception ()

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
