from __future__ import absolute_import

from wbsdevops import yamlx

from wbsdevops.schema import SchemaGroup, SchemaField

def args (prev_sub_parser):

	parser = prev_sub_parser.add_parser ("admin")
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
		help = "name of admin to create")

	parser.add_argument (
		"--full-name",
		help = "full name of admin")

	parser.add_argument (
		"--ssh-key",
		help = "public ssh key to identify admin")

def do_create (context, args):

	admin_path = "/admin/%s" % args.name

	if context.client.exists (admin_path):

		raise Exception (
			"Admin already exists: %s" % args.name)

	admin_data_mappings = {
		"admin_name": "name",
		"admin_full_name": "full_name",
	}

	arg_vars = vars (args)

	admin_data = {}

	for target, source in admin_data_mappings.items ():

		if not arg_vars [source]:
			continue

		admin_data [target] = arg_vars [source]

	context.client.set_yaml (
		"%s/data" % admin_path,
		admin_data,
		context.schemas ["admin"])

	if args.ssh_key:

		with open (args.ssh_key) as file_handle:
			ssh_key = file_handle.read ()

		context.client.set_raw (
			key = "%s/ssh-key" % admin_path,
			value = ssh_key)

	print "Created admin %s" % args.name

def schemas (schemas):

	schemas.define ("admin", [

		SchemaGroup ([

			SchemaField (
				name = "admin_name",
				required = True),

			SchemaField (
				name = "admin_full_name",
				required = False),

		]),

	])

# ex: noet ts=4 filetype=yaml
