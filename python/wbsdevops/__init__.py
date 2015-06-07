from __future__ import absolute_import
from __future__ import unicode_literals

from wbsdevops import certificate
from wbsdevops import core
from wbsdevops import generic
from wbsdevops import tools

from wbsdevops.certificate import Certificate
from wbsdevops.certificate import CertificateAuthority
from wbsdevops.certificate import CertificateDatabase

from wbsdevops.generic import GenericContext
from wbsdevops.generic import GenericCollection
from wbsdevops.generic import GenericCommand

from wbsdevops.tools import Client

modules = [
	certificate,
	core,
	generic,
	tools,
]

def args (sub_parsers):

	for module in modules:
		module.args (sub_parsers)

# ex: noet ts=4 filetype=yaml
