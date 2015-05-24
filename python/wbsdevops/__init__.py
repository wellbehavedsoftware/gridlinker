from __future__ import absolute_import

from wbsdevops import ansible
from wbsdevops import certificate
from wbsdevops import env
from wbsdevops import etcd
from wbsdevops import host

from wbsdevops.certificate import Certificate
from wbsdevops.certificate import CertificateAuthority
from wbsdevops.certificate import CertificateDatabase
from wbsdevops.client import Client
from wbsdevops.context import GenericContext

from wbsdevops.schema import Schema
from wbsdevops.schema import SchemaDatabase
from wbsdevops.schema import SchemaField
from wbsdevops.schema import SchemaGroup

def args (sub_parsers):

	ansible.args (sub_parsers)
	certificate.args (sub_parsers)
	env.args (sub_parsers)
	etcd.args (sub_parsers)
	host.args (sub_parsers)

def schemas (schemas):

	certificate.schemas (schemas)
