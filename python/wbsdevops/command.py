from __future__ import absolute_import

class CollectionCommand:

	def __init__ (self, helper):

		self.helper = helper

	def args (self, prev_sub_parser):

		parser = prev_sub_parser.add_parser (
			self.helper.name,
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

		parser.add_argument (
			"--name",
			required = True,
			help = "name of %s to create" % self.helper.name)

		self.helper.args_create (parser)

	def do_create (self, context, args):

		collection = self.helper.get_collection (context)

		if collection.exists (args.name):

			raise Exception (
				"%s already exists: %s" % (
					self.helper.name.title (),
					args.name))

		record_data = {}

		self.helper.do_create (context, args, record_data)

		collection.set (args.name, record_data)

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

		parser.add_argument (
			"--name",
			required = True,
			help = "name of %s to update" % self.helper.name)

		self.helper.args_update (parser)

	def do_update (self, context, args):

		collection = self.helper.get_collection (context)

		if not collection.exists (args.name):

			raise Exception (
				"%s does not exist: %s" % (
					self.helper.name.title (),
					args.name))

		record_data = collection.get (args.name)

		self.helper.do_update (context, args, record_data)

		collection.set (args.name, record_data)

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

	def args_common (self, parser):

		pass

	def do_common (self, context, args, record_data):

		pass

	def args_create (self, parser):

		self.args_common (parser)

	def do_create (self, context, args, record_data):

		self.do_common (context, args, record_data)

	def args_update (self, parser):

		self.args_common (parser)

	def do_update (self, context, args, record_data):

		self.do_common (context, args, record_data)

# ex: noet ts=4 filetype=yaml
