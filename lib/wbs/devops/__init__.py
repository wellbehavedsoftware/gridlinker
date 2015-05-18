from __future__ import absolute_import

import wbs.devops.certauthority
import wbs.devops.certdatabase
import wbs.devops.etcd
import wbs.devops.host

from wbs.devops.certauthority import CertificateAuthority
from wbs.devops.certdatabase import CertificateDatabase

from wbs.devops.client import Client

from wbs.devops.schema import Schema
from wbs.devops.schema import SchemaDatabase
from wbs.devops.schema import SchemaField
from wbs.devops.schema import SchemaGroup

def standard_commands (sub_parsers):

	certificate_parser = sub_parsers.add_parser ("certificate")
	certificate_sub_parsers = certificate_parser.add_subparsers ()

	wbs.devops.certauthority.args (certificate_sub_parsers)
	wbs.devops.certdatabase.args (certificate_sub_parsers)

	wbs.devops.etcd.args (sub_parsers)
	wbs.devops.host.args (sub_parsers)

def standard_schemas (schemas):

	wbs.devops.certauthority.add_schemas (schemas)
	wbs.devops.certdatabase.add_schemas (schemas)
