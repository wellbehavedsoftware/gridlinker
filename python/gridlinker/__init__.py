from __future__ import absolute_import
from __future__ import unicode_literals

from gridlinker import ansible

from gridlinker import certificate
from gridlinker.certificate import AlreadyExistsError
from gridlinker.certificate import CertificateAuthority
from gridlinker.certificate import CertificateDatabase

from gridlinker import core
from gridlinker.core import metadata
from gridlinker.core import GenericContext
from gridlinker.core import Inventory

from gridlinker import data
from gridlinker import flask

def args (sub_parser):

	ansible.args (sub_parser)
	certificate.args (sub_parser)
	data.args (sub_parser)
	etcd.args (sub_parser)
	tools.args (sub_parser)
	flask.args (sub_parser)

# ex: noet ts=4 filetype=yaml
