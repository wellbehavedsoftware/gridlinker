from __future__ import absolute_import
from __future__ import unicode_literals

from gridlinker.tools import ansible
from gridlinker.tools import client
from gridlinker.tools import etcd
from gridlinker.tools import ssh

from gridlinker.tools.client import Client

modules = [
	ansible,
	client,
	etcd,
	ssh,
]

def args (sub_parsers):

	for module in modules:
		module.args (sub_parsers)

# ex: noet ts=4 filetype=python
