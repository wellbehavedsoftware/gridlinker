from __future__ import absolute_import
from __future__ import unicode_literals

from gridlinker.etcd import client
from gridlinker.etcd.client import EtcdClient

from gridlinker.etcd import collection
from gridlinker.etcd.collection import GenericCollection

from gridlinker.etcd import tools

def args (parser):
	tools.args (parser)

# ex: noet ts=4 filetype=yaml
