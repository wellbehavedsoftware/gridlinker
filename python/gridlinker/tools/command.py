from __future__ import absolute_import
from __future__ import unicode_literals

import os
import sys
import tempfile

from wbs import generate_password
from wbs import print_table
from wbs import yamlx

from wbs import ReportableError

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
		self.args_remove (next_sub_parsers)
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

		parser.add_argument (
			"--update-existing",
			action = "store_true",
			help = "update existing {0} if present".format (self.helper.name))

	def do_create (self, context, args):

		collection = self.helper.get_collection (context)

		# determine name

		unique_name = self.helper.create_unique_name (context, args)

		if collection.exists_slow (unique_name):

			if not args.update_existing:

				raise Exception (
					"%s already exists: %s" % (
						self.helper.name.title (),
						unique_name))

			record_data = collection.get_slow (unique_name)

			already_exists = True

		else:

			record_data = {
				"identity": {
					"type": collection.type,
					"name": args.name,
				},
			}

			already_exists = False

		# set provided values

		# edit resource

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

		self.helper.update_record (context, args, record_data)

		# verify resource

		self.helper.verify (context, unique_name, record_data)

		# create resource

		collection.set (unique_name, record_data)

		self.helper.update_files (context, args, unique_name, collection)

		# display a message

		if already_exists:

			print ("Updated %s %s" % (
				self.helper.name,
				unique_name))

		else:

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

			if not self.helper.filter_record (args, record_name, record_data, context, self.helper):
				continue

			record_names.append (record_name)
			records_by_name [record_name] = record_data

		record_names = sorted (record_names)

		rows = [
			dict ([
				(
					column.name,
					column.get (context, self.helper, records_by_name [record_name])
					if column.exists (context, self.helper, records_by_name [record_name])
					else ""
				)
				for column in columns
			])
			for record_name in record_names
		]

		print_table (columns, rows, sys.stdout)

	def args_remove (self, sub_parsers):

		parser = sub_parsers.add_parser (
			"remove",
			help = "Remove one or more {0}".format (self.helper.name),
			description = """
				Remove a specific {0} or {0}s. To remove a single {0}, provide
				its fully qualified "--name". To remove a group, provide one or
				more other specifiers, eg "--class". This will remove all of the
				matching resources.
			""".format (self.helper.name))

		parser.set_defaults (
			func = self.do_remove)

		self.helper.args_remove (parser)

	def do_remove (self, context, args):

		collection = self.helper.get_collection (context)

		columns = self.helper.get_columns (context)

		# find records

		record_names = []
		records_by_name = {}

		for record_name, record_data \
		in collection.get_all_list_quick ():

			if not self.helper.filter_record (args, record_name, record_data, context, self.helper):
				continue

			record_names.append (record_name)
			records_by_name [record_name] = record_data

		record_names = sorted (record_names)

		for record_name in record_names:

			collection.remove (record_name)

			print ("Removed %s" % record_name)

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

			if not collection.exists_slow (args.name):

				raise Exception (
					"%s does not exist: %s" % (
						self.helper.name.title (),
						args.name))

			all_records = [
				(args.name, collection.get_slow (args.name))
			]

		else:

			all_records = collection.get_all_list ()

		filtered_records = [
			(record_name, record_data)
			for record_name, record_data in all_records
			if self.helper.filter_record (args, record_name, record_data, context, self.helper)
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

		if not collection.exists_slow (args.name):

			raise Exception (
				"%s does not exist: %s" % (
					self.helper.name.title (),
					args.name))

		record_data = collection.get_slow (args.name)

		with tempfile.NamedTemporaryFile () as temp_file:

			record_yaml = collection.to_yaml (record_data)

			temp_file.write (record_yaml)
			temp_file.flush ()

			if "VISUAL" in os.environ:
				editor = os.environ ["VISUAL"]

			elif "EDITOR" in os.environ:
				editor = os.environ ["EDITOR"]

			else:
				raise ReportableError (
					"editor_not_configured")

			os.system ("%s %s" % (editor, temp_file.name))

			with open (temp_file.name, "r") as temp_file_again:
				record_yaml = temp_file_again.read ()

		record_data = yamlx.parse (record_yaml)

		collection.set (args.name, record_data)

	def args_show (self, sub_parsers):

		parser = sub_parsers.add_parser (
			"show",
			help = "show the data for a {0}".format (self.helper.name))

		parser.set_defaults (
			func = self.do_show)

		self.helper.args_show (parser)

	def do_show (self, context, args):

		collection = self.helper.get_collection (context)

		record_data = collection.get_slow (args.name)

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

	def args_remove (self, parser):

		for custom_arg in self.custom_args:
			if hasattr (custom_arg, "args_remove"):
				custom_arg.args_remove (parser, self)

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

				custom_arg.update_record (
					arg_vars,
					record_data,
					context,
					self)

	def update_files (self, context, args, unique_name, collection):

		arg_vars = vars (args)

		for custom_arg in self.custom_args:
			if hasattr (custom_arg, "update_files"):
				custom_arg.update_files (arg_vars, unique_name, context, self)

	def get_collection (self, context):

		return getattr (context, self.collection_name)

	def get_columns (self, context):

		return self.custom_columns

	def filter_record (self, args, record_name, record_data, context, helper):

		arg_vars = vars (args)

		for custom_arg in self.custom_args:
			if hasattr (custom_arg, "filter_record") \
			and not custom_arg.filter_record (arg_vars, record_name, record_data, context, helper):
				return False

		return True

# ex: noet ts=4 filetype=yaml
