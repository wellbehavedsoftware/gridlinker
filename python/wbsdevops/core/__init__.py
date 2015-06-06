from __future__ import absolute_import
from __future__ import unicode_literals

from wbsdevops.core import group
from wbsdevops.core import resource
from wbsdevops.core import sshkey

modules = [
	group,
	resource,
	sshkey,
]

def args (sub_parsers):

	for module in modules:
		module.args (sub_parsers)

# ex: noet ts=4 filetype=python
