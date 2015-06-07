from __future__ import absolute_import
from __future__ import unicode_literals

from gridlinker import certificate
from gridlinker import core
from gridlinker import env
from gridlinker import generic
from gridlinker import tools

from gridlinker.certificate import Certificate
from gridlinker.certificate import CertificateAuthority
from gridlinker.certificate import CertificateDatabase

from gridlinker.generic import GenericContext
from gridlinker.generic import GenericCollection
from gridlinker.generic import GenericCommand

from gridlinker.tools import Client

modules = [
	certificate,
	core,
	env,
	generic,
	tools,
]

def args (sub_parsers):

	for module in modules:
		module.args (sub_parsers)

# ex: noet ts=4 filetype=yaml
