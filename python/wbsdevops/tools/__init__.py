from __future__ import absolute_import

from wbsdevops.tools import ansible
from wbsdevops.tools import client
from wbsdevops.tools import etcd

from wbsdevops.tools.client import Client

modules = [
	ansible,
	client,
	etcd,
]

def args (sub_parsers):

	for module in modules:
		module.args (sub_parsers)

# ex: noet ts=4 filetype=python
