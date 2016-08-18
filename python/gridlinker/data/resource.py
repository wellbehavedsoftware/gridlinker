from __future__ import absolute_import
from __future__ import unicode_literals

from wbs import ReportableError

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

	def verify (self, context, resource_name, resource_data):

		errors = []

		class_name = resource_data ["identity"] ["class"]
		class_data = context.local_data ["classes"] [class_name]

		# check resource name

		expected_resource_name = "%s/%s" % (
			class_data ["class"] ["namespace"],
			resource_data ["identity"] ["name"])

		if resource_name != expected_resource_name:

			errors.append (ReportableError (
				"resource_name_mismatch",
				resource_name = resource_name,
				expected_resource_name = expected_resource_name))

		# check parentage

		if "parent_namespace" in class_data ["class"]:

			if not "parent" in resource_data ["identity"]:

				errors.append (ReportableError (
					"resource_parent_not_set",
					resource_name = resource_name,
					class_name = class_name))

			else:

				parent_name = "%s/%s" % (
					class_data ["class"] ["parent_namespace"],
					resource_data ["identity"] ["parent"])

				if not context.resources.exists_quick (parent_name):

					errors.append (ReportableError (
						"resource_parent_does_not_exist",
						resource_name = resource_name,
						parent_name = parent_name))

		else:

			if "parent" in resource_data ["identity"]:

				errors.append (ReportableError (
					"resource_parent_set",
					resource_name = resource_name,
					class_name = class_name))

		if errors:

			raise errors [0]

resource_command = GenericCommand (

	ResourceHelper (

		name = "resource",
		help = "manage resource definitions",

		custom_args = [

			ArgumentGroup (
				label = "resource identity",
				arguments = [

				ClassArgument (),
				NamespaceArgument (),
				NameArgument (),
				ParentArgument (),
				IndexArgument (),

			]),

			ArgumentGroup (
				label = "arbitrary configuration",
				arguments = [

				MiscSetArgument (),
				MiscSetJsonArgument (),
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
				section = "vpn",
				name = "address",
				label = "VPN IP",
				default = True),

		],

	)

)

def args (sub_parsers):

	resource_command.args (sub_parsers)

# ex: noet ts=4 filetype=yaml
