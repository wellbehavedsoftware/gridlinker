def args (sub_parsers):

	args_env (sub_parsers)

def args_env (sub_parsers):

	parser = sub_parsers.add_parser (
		"env")

	parser.set_defaults (
		func = do_env)

def do_env (context, args):

	for key in sorted (context.env.keys ()):
		print "export %s=\"%s\"" % (key, context.env [key])
