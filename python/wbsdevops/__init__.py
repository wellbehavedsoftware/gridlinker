from __future__ import absolute_import

from wbsdevops import admin
from wbsdevops import ansible
from wbsdevops import certificate
from wbsdevops import env
from wbsdevops import etcd
from wbsdevops import group
from wbsdevops import host
from wbsdevops import sshkey

from wbsdevops.certificate import Certificate
from wbsdevops.certificate import CertificateAuthority
from wbsdevops.certificate import CertificateDatabase
from wbsdevops.client import Client
from wbsdevops.context import GenericContext
from wbsdevops.collection import Collection

from wbsdevops.schema import Schema
from wbsdevops.schema import SchemaDatabase
from wbsdevops.schema import SchemaField
from wbsdevops.schema import SchemaGroup

modules = [
	admin,
	ansible,
	certificate,
	env,
	etcd,
	group,
	host,
	sshkey,
]

def args (sub_parsers):

	for module in modules:
		module.args (sub_parsers)

# ex: noet ts=4 filetype=yaml
