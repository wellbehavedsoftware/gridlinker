from __future__ import absolute_import
from __future__ import unicode_literals

from gridlinker import ansible

from gridlinker import certificate

from gridlinker import core
from gridlinker.core import metadata
from gridlinker.core import GenericContext

from gridlinker import data

def args (sub_parser):

	ansible.args (sub_parser)
	certificate.args (sub_parser)
	data.args (sub_parser)
	etcd.args (sub_parser)
	tools.args (sub_parser)

# ex: noet ts=4 filetype=yaml
