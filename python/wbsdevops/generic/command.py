from __future__ import absolute_import

import sys

from wbsmisc import generate_password

class GenericCommand:

	def __init__ (self, helper):

		self.helper = helper

	def args (self, prev_sub_parser):

		parser = prev_sub_parser.add_parser (
			self.helper.command_name,
			help = self.helper.help,
			description = self.helper.description)

		next_sub_parsers = parser.add_subparsers ()

		self.args_create (next_sub_parsers)
		self.args_list (next_sub_parsers)
		self.args_show (next_sub_parsers)
		self.args_update (next_sub_parsers)

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

	def args_list (self, sub_parsers):

		parser = sub_parsers.add_parser (
			"list",
			help = "list some or all {0}s".format (self.helper.name),
			description = """
				List some or all {0}s. With no extra arguments, this command
				will provide a list of all of the {0}s which are defined. Other
				options can be provided to filter the list, to modify the
				columns displayed, to modify the order and to output the data in
				a different format.
			""".format (self.helper.name))

		parser.set_defaults (
			func = self.do_list)

	def do_list (self, context, args):

		collection = self.helper.get_collection (context)

		columns = self.helper.get_columns (context)

		# find records

		record_names = []
		records_by_name = {}

		for record_name, record_data \
		in collection.get_all_list ():

			record_names.append (record_name)
			records_by_name [record_name] = record_data

		record_names = sorted (record_names)

		# calculate column sizes

		column_sizes = {}

		for column in columns:

			max_size = len (column)

			for record_data in records_by_name.values ():

				if not column in record_data:
					continue

				value = record_data [column]
				length = len (value)

				if length > max_size:
					max_size = length

			column_sizes [column] = max_size

		# show headings

		sys.stdout.write ("\n ")

		for column in columns:
			column_size = column_sizes [column]
			sys.stdout.write (column.ljust (column_size + 1))

		sys.stdout.write ("\n")

		# show line

		sys.stdout.write ("-")

		for column in columns:
			column_size = column_sizes [column]
			sys.stdout.write ("-" * (column_size + 1))

		sys.stdout.write ("\n")

		# show data

		for record_name in record_names:

			record_data = records_by_name [record_name]

			sys.stdout.write (" ")

			for column in columns:

				column_size = column_sizes [column]

				if column in record_data:
					value = record_data [column]
				else:
					value = ""

				sys.stdout.write (value.ljust (column_size + 1))

			sys.stdout.write ("\n")		

		sys.stdout.write ("\n")		

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

class CommandHelper:

	def __init__ (self,

		name,
		command_name = None,
		collection_name = None,

		help = None,
		description = None,

		custom_args = [],
		custom_columns = None,

	):

		self.name = name
		self.command_name = command_name or name
		self.collection_name = collection_name or name.replace ('-', '_') + "s"

		self.help = help
		self.description = description

		self.custom_args = custom_args
		self.custom_columns = custom_columns or [ name + "_name" ]

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

	def get_columns (self, context):

		return self.custom_columns

# ex: noet ts=4 filetype=yaml
