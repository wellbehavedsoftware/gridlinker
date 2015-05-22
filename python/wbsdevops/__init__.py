from __future__ import absolute_import

from wbsdevops import ansible
from wbsdevops import certauthority
from wbsdevops import certdatabase
from wbsdevops import env
from wbsdevops import etcd
from wbsdevops import host

from wbsdevops.certauthority import CertificateAuthority
from wbsdevops.certdatabase import CertificateDatabase
from wbsdevops.client import Client
from wbsdevops.context import GenericContext

from wbsdevops.schema import Schema
from wbsdevops.schema import SchemaDatabase
from wbsdevops.schema import SchemaField
from wbsdevops.schema import SchemaGroup

def args (sub_parsers):

	certificate_parser = sub_parsers.add_parser ("certificate")
	certificate_sub_parsers = certificate_parser.add_subparsers ()

	certauthority.args (certificate_sub_parsers)
	certdatabase.args (certificate_sub_parsers)

	ansible.args (sub_parsers)
	env.args (sub_parsers)
	etcd.args (sub_parsers)
	host.args (sub_parsers)

def schemas (schemas):

	certauthority.add_schemas (schemas)
	certdatabase.add_schemas (schemas)
