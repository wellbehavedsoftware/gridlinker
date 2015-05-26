from __future__ import absolute_import

from wbsdevops.core import admin
from wbsdevops.core import group
from wbsdevops.core import host
from wbsdevops.core import sshkey

modules = [
	admin,
	group,
	host,
	sshkey,
]

def args (sub_parsers):

	for module in modules:
		module.args (sub_parsers)

# ex: noet ts=4 filetype=python
