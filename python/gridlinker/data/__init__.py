from __future__ import absolute_import
from __future__ import unicode_literals

from gridlinker.data import group
from gridlinker.data import resource

def args (parser):
	group.args (parser)
	resource.args (parser)

# ex: noet ts=4 filetype=yaml
