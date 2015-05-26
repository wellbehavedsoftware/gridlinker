from wbsdevops.amazon import account
from wbsdevops.amazon import balancer
from wbsdevops.amazon import vpc

modules = [
	account,
	balancer,
	vpc,
]

def args (prev_sub_parsers):

	parser = prev_sub_parsers.add_parser (
		"amazon",
		help = "manage amazon clould services",
		description = """
			This group of commands can be used to manage amazon cloud services.
		""")

	next_sub_parsers = parser.add_subparsers ()

	for module in modules:
		module.args (next_sub_parsers)

# ex: noet ts=4 filetype=python
