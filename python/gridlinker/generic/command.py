from __future__ import absolute_import
from __future__ import unicode_literals

import os
import sys
import tempfile

from wbs import generate_password
from wbs import yamlx

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
		self.args_edit (next_sub_parsers)
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

		unique_name = self.helper.get_unique_name (context, args)

		if collection.exists (unique_name):

			raise Exception (
				"%s already exists: %s" % (
					self.helper.name.title (),
					unique_name))

		record_data = {
			"identity": {
				"type": collection.type,
			},
		}

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

		collection.set (unique_name, record_data)

		self.helper.update_files (context, args, unique_name, collection)

		print ("Created %s %s" % (
			self.helper.name,
			unique_name))

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

		self.helper.args_list (parser)

	def do_list (self, context, args):

		collection = self.helper.get_collection (context)

		columns = self.helper.get_columns (context)

		# find records

		record_names = []
		records_by_name = {}

		for record_name, record_data \
		in collection.get_all_list_quick ():

			if not self.helper.filter_record (context, args, record_data):
				continue

			record_names.append (record_name)
			records_by_name [record_name] = record_data

		record_names = sorted (record_names)

		# calculate column sizes

		column_sizes = {}

		for column in columns:

			max_size = len (column.label)

			for record_data in records_by_name.values ():

				if not column.section in record_data:
					continue

				if not column.name in record_data [column.section]:
					continue

				value = record_data [column.section] [column.name]
				length = len (value)

				if length > max_size:
					max_size = length

			column_sizes [column.name] = max_size

		# show headings

		sys.stdout.write ("\n ")

		for column in columns:
			column_size = column_sizes [column.name]
			sys.stdout.write (column.label.ljust (column_size + 1))

		sys.stdout.write ("\n")

		# show line

		sys.stdout.write ("-")

		for column in columns:
			column_size = column_sizes [column.name]
			sys.stdout.write ("-" * (column_size + 1))

		sys.stdout.write ("\n")

		# show data

		for record_name in record_names:

			record_data = records_by_name [record_name]

			sys.stdout.write (" ")

			for column in columns:

				column_size = column_sizes [column.name]

				if not column.section in record_data:
					value = ""
				elif not column.name in record_data [column.section]:
					value = ""
				else:
					value = record_data [column.section] [column.name]

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

		if args.name:

			unique_name = self.helper.get_unique_name (context, args)

			if not collection.exists (unique_name):

				raise Exception (
					"%s does not exist: %s" % (
						self.helper.name.title (),
						unique_name))

			all_records = [
				(unique_name, collection.get (unique_name))
			]

		else:

			all_records = collection.get_all_list ()

		filtered_records = [
			(record_name, record_data)
			for record_name, record_data in all_records
			if self.helper.filter_record (context, args, record_data)
		]

		for unique_name, record_data in filtered_records:

			self.helper.update_record (context, args, record_data)

			collection.set (record_name, record_data)

			self.helper.update_files (context, args, unique_name, collection)

			print ("Updated %s %s" % (
				self.helper.name,
				record_name))

	def args_edit (self, sub_parsers):

		parser = sub_parsers.add_parser (
			"edit",
			help = "edit an existing {0}".format (self.helper.name),
			description = """
				Edit an existing {0}. This command opens up a text editor with
				the data of a {0} from the admin database, allowing you to make
				changes by hand. It will report an error if the {0} does not
				already exist.
			""".format (self.helper.name))

		parser.set_defaults (
			func = self.do_edit)

		self.helper.args_edit (parser)

	def do_edit (self, context, args):

		collection = self.helper.get_collection (context)

		unique_name = self.helper.get_unique_name (context, args)

		if not collection.exists_slow (unique_name):

			raise Exception (
				"%s does not exist: %s" % (
					self.helper.name.title (),
					unique_name))

		record_data = collection.get_slow (unique_name)

		with tempfile.NamedTemporaryFile () as temp_file:

			record_yaml = collection.to_yaml (record_data)

			temp_file.write (record_yaml)
			temp_file.flush ()

			os.system ("%s %s" % (os.environ ["EDITOR"], temp_file.name))

			with open (temp_file.name, "r") as temp_file_again:
				record_yaml = temp_file_again.read ()

		record_data = yamlx.parse (record_yaml)

		collection.set (unique_name, record_data)

	def args_show (self, sub_parsers):

		parser = sub_parsers.add_parser (
			"show",
			help = "show the data for a {0}".format (self.helper.name))

		parser.set_defaults (
			func = self.do_show)

		self.helper.args_show (parser)

	def do_show (self, context, args):

		collection = self.helper.get_collection (context)

		unique_name = self.helper.get_unique_name (context, args)

		record_data = collection.get_slow (unique_name)

		record_yaml = collection.to_yaml (record_data)

		print (record_yaml)

class CommandHelper:

	def __init__ (self,

		name,
		command_name = None,
		short_name = None,
		collection_name = None,

		help = None,
		description = None,

		custom_args = [],
		custom_columns = [],

	):

		self.name = name
		self.short_name = short_name or name.replace ('-', '_')
		self.command_name = command_name or name
		self.collection_name = collection_name or name.replace ('-', '_') + "s"

		self.help = help
		self.description = description

		self.custom_args = custom_args
		self.custom_columns = custom_columns

	def args_create (self, parser):

		for custom_arg in self.custom_args:
			if hasattr (custom_arg, "args_create"):
				custom_arg.args_create (parser, self)

	def args_edit (self, parser):

		for custom_arg in self.custom_args:
			if hasattr (custom_arg, "args_edit"):
				custom_arg.args_edit (parser, self)

	def args_list (self, parser):

		for custom_arg in self.custom_args:
			if hasattr (custom_arg, "args_list"):
				custom_arg.args_list (parser, self)

	def args_show (self, parser):

		for custom_arg in self.custom_args:
			if hasattr (custom_arg, "args_show"):
				custom_arg.args_show (parser, self)

	def args_update (self, parser):

		for custom_arg in self.custom_args:
			if hasattr (custom_arg, "args_update"):
				custom_arg.args_update (parser, self)

	def update_record (self, context, args, record_data):

		arg_vars = vars (args)

		for custom_arg in self.custom_args:
			if hasattr (custom_arg, "update_record"):
				custom_arg.update_record (arg_vars, record_data, self)

	def update_files (self, context, args, unique_name, collection):

		arg_vars = vars (args)

		for custom_arg in self.custom_args:
			if hasattr (custom_arg, "update_files"):
				custom_arg.update_files (arg_vars, unique_name, collection, self)

	def get_collection (self, context):

		return getattr (context, self.collection_name)

	def get_columns (self, context):

		return self.custom_columns

	def filter_record (self, context, args, record_data):

		arg_vars = vars (args)

		for custom_arg in self.custom_args:
			if hasattr (custom_arg, "filter_record") \
			and not custom_arg.filter_record (arg_vars, record_data, self):
				return False

		return True

# ex: noet ts=4 filetype=yaml
