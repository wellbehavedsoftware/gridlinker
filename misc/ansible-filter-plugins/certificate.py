from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import importlib
import os

from wbs import lazy_property

__all__ = [
	"FilterModule",
]

class FilterModule (object):

	@lazy_property
	def support (self):

		module = (
			importlib.import_module (
				os.environ ["GRIDLINKER_SUPPORT"]))

		return module.support

	@lazy_property
	def context (self):

		return self.support.get_context ()

	@lazy_property
	def client (self):

		return self.context.client

	def certificate (self, main_path):

		return self.client.get_raw (
			"%s/certificate" % (
				main_path))

	def private_key (self, main_path):

		return self.client.get_raw (
			"%s/key" % (
				main_path))

	def certificate_and_chain (self, main_path):

		certificates = []

		for certificate_path in [
			"/certificate",
			"/chain/0",
			"/chain/1",
			"/chain/2",
		]:

			certificates.append (
				self.client.get_raw (
					"%s%s" % (
						main_path,
						certificate_path)))

		return "".join (certificates)

	def certificate_and_key_and_chain (self, main_path):

		certificates = []

		for certificate_path in [
			"/certificate",
			"/key",
			"/chain/0",
			"/chain/1",
			"/chain/2",
		]:

			certificates.append (
				self.client.get_raw (
					"%s%s" % (
						main_path,
						certificate_path)))

		return "".join (certificates)

	def filters (self):

		return dict ([
			( name, getattr (self, name) )
			for name
			in [
				"certificate",
				"certificate_and_chain",
				"certificate_and_key_and_chain",
				"private_key",
			]
		])

# ex: noet ts=4 filetype=python
