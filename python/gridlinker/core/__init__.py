from __future__ import absolute_import
from __future__ import unicode_literals

from gridlinker.core import group
from gridlinker.core import resource
from gridlinker.core import sshkey

modules = [
	group,
	resource,
	sshkey,
]

def args (sub_parsers):

	for module in modules:
		module.args (sub_parsers)

# ex: noet ts=4 filetype=python
