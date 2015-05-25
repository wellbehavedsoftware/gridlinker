from __future__ import absolute_import

from wbsdevops import yamlx
from wbsdevops.schema import SchemaGroup, SchemaField

from wbsmisc import generate_password

def args (prev_sub_parser):

	parser = prev_sub_parser.add_parser (
		"group")

	next_sub_parsers = parser.add_subparsers ()

	args_create (next_sub_parsers)

def args_create (sub_parsers):

	parser = sub_parsers.add_parser (
		"create")

	parser.set_defaults (
		func = do_create)

	parser.add_argument (
		"--name",
		required = True,
		help = "name of group to create")

	parser.add_argument (
		"--description",
		help = "user-friendly description")

	parser.add_argument (
		"--set",
		action = "append",
		nargs = 2,
		default = [],
		help = "miscellaneous value to store")

	parser.add_argument (
		"--generate-password",
		action = "append",
		default = [],
		help = "generate random password to store")

def do_create (context, args):

	group_path = "/group/%s" % args.name

	if context.client.exists (group_path):

		raise Exception (
			"Group already exists: %s" % args.name)

	group_data_mappings = {
		"group_name": "name",
		"group_description": "description",
	}

	arg_vars = vars (args)

	group_data = {}

	for target, source in group_data_mappings.items ():

		if not arg_vars [source]:
			continue

		group_data [target] = arg_vars [source]

	for key, value in args.set:

		group_data [key] = value

	for key in args.generate_password:

		group_data [key] = generate_password ()

	context.client.set_yaml (
		"%s/data" % group_path,
		group_data,
		context.schemas ["group"])

	print "Created group %s" % args.name

def schemas (schemas):

	schemas.define ("group", [

		SchemaGroup ([

			SchemaField (
				name = "group_name",
				required = True),

			SchemaField (
				name = "group_description",
				required = False),

		]),

	])

# ex: noet ts=4 filetype=yaml
