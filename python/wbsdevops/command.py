from __future__ import absolute_import

from wbsmisc import generate_password

class CollectionCommand:

	def __init__ (self, helper):

		self.helper = helper

	def args (self, prev_sub_parser):

		parser = prev_sub_parser.add_parser (
			self.helper.command_name,
			help = self.helper.help,
			description = self.helper.description)

		next_sub_parsers = parser.add_subparsers ()

		self.args_create (next_sub_parsers)
		self.args_update (next_sub_parsers)
		self.args_show (next_sub_parsers)

	def args_create (self, sub_parsers):

		parser = sub_parsers.add_parser (
			"create",
			help = "create a new {0}".format (self.helper.name),
			description = """
				Create a new {0}. This command takes the name of a {0} and
				various other arguments which are stored in the admin database.
				It will report an error if the {0} already exists.
			""".format (self.helper.name))

		parser.set_defaults (
			func = self.do_create)

		self.helper.args_create (parser)

		parser.add_argument (
			"--edit",
			action = "store_true",
			help = "edit {0} data before creating".format (self.helper.name))

	def do_create (self, context, args):

		collection = self.helper.get_collection (context)

		if collection.exists (args.name):

			raise Exception (
				"%s already exists: %s" % (
					self.helper.name.title (),
					args.name))

		record_data = {}

		self.helper.update_record (context, args, record_data)

		if args.edit:

			temp_file = tempfile.NamedTemporaryFile ()

			record_yaml = collection.to_yaml (record_data)

			temp_file.write (record_yaml)
			temp_file.flush ()

			os.system ("%s %s" % (os.environ ["EDITOR"], temp_file.name))

			temp_again = open (temp_file.name, "r")
			record_yaml = temp_again.read ()

			record_data = yamlx.parse (record_yaml)

			temp_again.close ()

		collection.set (args.name, record_data)

		self.helper.update_files (context, args, collection)

		print "Created %s %s" % (
			self.helper.name,
			args.name)

	def args_update (self, sub_parsers):

		parser = sub_parsers.add_parser (
			"update",
			help = "update an existing {0}".format (self.helper.name),
			description = """
				Update an existing {0}. This command takes the name of a {0} and
				various other arguments which are stored in the admin database.
				It will report an error if the {0} does not already exist.
			""".format (self.helper.name))

		parser.set_defaults (
			func = self.do_update)

		self.helper.args_update (parser)

	def do_update (self, context, args):

		collection = self.helper.get_collection (context)

		if not collection.exists (args.name):

			raise Exception (
				"%s does not exist: %s" % (
					self.helper.name.title (),
					args.name))

		record_data = collection.get (args.name)

		self.helper.update_record (context, args, record_data)

		collection.set (args.name, record_data)

		self.helper.update_files (context, args, collection)

		print "Updated %s %s" % (
			self.helper.name,
			args.name)

	def args_show (self, sub_parsers):

		parser = sub_parsers.add_parser (
			"show",
			help = "show the data for a {0}".format (self.helper.name))

		parser.set_defaults (
			func = self.do_show)

		parser.add_argument (
			"--name",
			help = "{0} to show data for".format (self.helper.name))

	def do_show (self, context, args):

		collection = self.helper.get_collection (context)

		record_data = collection.get (args.name)

		record_yaml = collection.to_yaml (record_data)

		print record_yaml

class ArgumentGroup:

	def __init__ (self, label, arguments):

		self.label = label
		self.arguments = arguments

	def args_create (self, parser, helper):

		group = parser.add_argument_group (self.label)

		for argument in self.arguments:
			argument.args_create (group, helper)

	def args_update (self, parser, helper):

		group = parser.add_argument_group (self.label)

		for argument in self.arguments:
			argument.args_create (group, helper)

	def update_record (self, arg_vars, record_data):

		for argument in self.arguments:
			argument.update_record (arg_vars, record_data)

	def update_files (self, arg_vars, collection):

		for argument in self.arguments:
			argument.update_files (arg_vars, collection)

class SimpleArgument:

	def __init__ (self, argument, key, value_name, help):

		self.argument = argument
		self.key = key
		self.value_name = value_name
		self.help = help

		self.argument_name = argument [2:].replace ("-", "_")

	def args_create (self, parser, helper):

		parser.add_argument (
			self.argument,
			metavar = self.value_name,
			help = self.help)

	def args_update (self, parser, helper):

		parser.add_argument (
			self.argument,
			metavar = self.value_name,
			help = self.help)

	def update_record (self, arg_vars, record_data):

		value = arg_vars [self.argument_name]

		if value:
			record_data [self.key] = value

	def update_files (self, arg_vars, collection):

		pass

class AddListArgument:

	def __init__ (self, argument, key, help, value_name):

		self.argument = argument
		self.key = key
		self.help = help
		self.value_name = value_name

		self.argument_name = argument [2:].replace ("-", "_")

	def args_create (self, parser, helper):

		parser.add_argument (
			self.argument,
			action = "append",
			default = [],
			help = self.help,
			metavar = self.value_name)

	def args_update (self, parser, helper):

		parser.add_argument (
			self.argument,
			action = "append",
			default = [],
			help = self.help,
			metavar = self.value_name)

	def update_record (self, arg_vars, record_data):

		for value in arg_vars [self.argument_name]:

			if not self.key in record_data:
				record_data [self.key] = []

			record_data [self.key].append (value)

	def update_files (self, arg_vars, collection):

		pass

class AddDictionaryArgument:

	def __init__ (self, argument, key, help, key_name, value_name):

		self.argument = argument
		self.key = key
		self.help = help
		self.key_name = key_name
		self.value_name = value_name

		self.argument_name = argument [2:].replace ("-", "_")

	def args_create (self, parser, helper):

		parser.add_argument (
			self.argument,
			action = "append",
			default = [],
			nargs = 2,
			help = self.help,
			metavar = (self.key_name, self.value_name))

	def args_update (self, parser, helper):

		parser.add_argument (
			self.argument,
			action = "append",
			default = [],
			nargs = 2,
			help = self.help,
			metavar = (self.key_name, self.value_name))

	def update_record (self, arg_vars, record_data):

		for key, value in arg_vars [self.argument_name]:

			if not self.key in record_data:
				record_data [self.key] = {}

			record_data [self.key] [key] = value

	def update_files (self, arg_vars, collection):

		pass

class NameArgument:

	def __init__ (self, argument, key):

		self.argument = argument
		self.key = key

	def args_create (self, parser, helper):

		parser.add_argument (
			self.argument,
			required = True,
			help = "name of %s to create" % helper.name)

	def args_update (self, parser, helper):

		parser.add_argument (
			"--name",
			required = True,
			help = "name of %s to update" % helper.name)

	def update_record (self, arg_vars, record_data):

		record_data [self.key] = arg_vars ["name"]

	def update_files (self, arg_vars, collection):

		pass

class FileArgument:

	def __init__ (self, argument, path, help):

		self.argument = argument
		self.path = path
		self.help = help

		self.argument_name = argument [2:].replace ("-", "_")

	def args_create (self, parser, helper):

		parser.add_argument (
			self.argument,
			metavar = "FILE",
			help = self.help)

	def args_update (self, parser, helper):

		parser.add_argument (
			self.argument,
			metavar = "FILE",
			help = self.help)

	def update_record (self, arg_vars, record_data):

		pass

	def update_files (self, arg_vars, collection):

		value = arg_vars [self.argument_name]

		if not value:
			return

		with open (value) as file_handle:
			file_contents = file_handle.read ()

		collection.set_file (arg_vars ["name"], self.path, file_contents)

class SetArgument:

	def __init__ (self):

		pass

	def args_create (self, parser, helper):

		parser.add_argument (
			"--set",
			action = "append",
			nargs = 2,
			default = [],
			metavar = ("KEY", "VALUE"),
			help = "miscellaneous value to store")

	def args_update (self, parser, helper):

		parser.add_argument (
			"--set",
			action = "append",
			nargs = 2,
			default = [],
			help = "miscellaneous value to store")

	def update_record (self, arg_vars, record_data):

		for key, value in arg_vars ["set"]:
			record_data [key] = value

	def update_files (self, arg_vars, collection):

		pass

class GeneratePasswordArgument:

	def __init__ (self):

		pass

	def args_create (self, parser, helper):

		parser.add_argument (
			"--generate-password",
			action = "append",
			default = [],
			help = "generate random password to store")

	def args_update (self, parser, helper):

		parser.add_argument (
			"--generate-password",
			action = "append",
			default = [],
			help = "generate random password to store")

	def update_record (self, arg_vars, record_data):

		for key in arg_vars ["generate_password"]:
			record_data [key] = generate_password ()

	def update_files (self, arg_vars, collection):

		pass

class CommandHelper:

	def __init__ (self,

		name,
		command_name = None,
		collection_name = None,

		help = None,
		description = None,

		enable_description = False,
		enable_set = False,
		enable_generate_password = False,

		custom_args = [],

	):

		self.name = name
		self.command_name = command_name or name
		self.collection_name = collection_name or name.replace ('-', '_') + "s"

		self.help = help
		self.description = description

		self.enable_description = enable_description
		self.enable_set = enable_set
		self.enable_generate_password = enable_generate_password

		self.custom_args = custom_args

	def args_create (self, parser):

		for custom_arg in self.custom_args:
			custom_arg.args_create (parser, self)

	def args_update (self, parser):

		for custom_arg in self.custom_args:
			custom_arg.args_update (parser, self)

	def update_record (self, context, args, record_data):

		arg_vars = vars (args)

		for custom_arg in self.custom_args:
			custom_arg.update_record (arg_vars, record_data)

	def update_files (self, context, args, collection):

		arg_vars = vars (args)

		for custom_arg in self.custom_args:
			custom_arg.update_files (arg_vars, collection)

	def get_collection (self, context):

		return getattr (context, self.collection_name)

# ex: noet ts=4 filetype=yaml
