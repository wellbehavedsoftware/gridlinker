from __future__ import absolute_import
from __future__ import unicode_literals

import os
import subprocess
import sys
import tempfile

from wbs import env_resolve

def args (prev_sub_parsers):

	parser = prev_sub_parsers.add_parser (
		"flask",
		help = "tools to manage flask directly")

	next_sub_parsers = parser.add_subparsers ()

	args_flask_start (next_sub_parsers)
	args_flask_stop (next_sub_parsers)

def args_flask_start (sub_parsers):

	parser = sub_parsers.add_parser (
		"start",
		help = "starts the flask webserver")

	parser.set_defaults (
		func = do_flask_start)

	parser.add_argument (
		"rest",
		nargs = "*")

def do_flask_start (context, args):

	result = subprocess.call (
		[ "sudo", "python", "%s/src/wbsSiteAdmin.py" % context.webserver_home])

	sys.exit (result)

def args_flask_stop (sub_parsers):

	parser = sub_parsers.add_parser (
		"stop",
		help = "stops the flask webserver")

	parser.set_defaults (
		func = do_flask_stop)

	parser.add_argument (
		"rest",
		nargs = "*")

def do_flask_stop (context, args):

	result = subprocess.call (
		[ "ls" ] + args.rest)

	sys.exit (result)

# ex: noet ts=4 filetype=yaml
