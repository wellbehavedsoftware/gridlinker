from __future__ import absolute_import
from __future__ import unicode_literals

def args (sub_parsers):

	args_ssh (sub_parsers)

def args_ssh (prev_sub_parsers):

	parser = prev_sub_parsers.add_parser (
		"ssh",
		help = "ssh to a host")

	parser.set_defaults (
		func = do_ssh)

	parser.add_argument (
		"host",
		metavar = "HOST",
		help = "host to ssh to")

def do_ssh (context, args):

	print (args.host)

# ex: noet ts=4 filetype=yaml
