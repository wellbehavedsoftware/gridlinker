from __future__ import absolute_import
from __future__ import unicode_literals

import importlib
import os

from ansible import utils

class LookupModule (object):

	def __init__ (self, basedir = None, ** kwargs):

		self.basedir = basedir

		self.support = importlib.import_module (os.environ ["GRIDLINKER_SUPPORT"]).support
		self.context = self.support.get_context ()

		self.client = self.context.client

	def run (self, terms, inject = None, ** kwargs):

		terms = utils.listify_lookup_plugin_terms (
			terms,
			self.basedir,
			inject)

		if isinstance (terms, basestring):
			terms = [ terms ]

		ret = []

		for term in terms:

			key = term.split () [0]

			value = self.client.get_raw (key)

			ret.append (value)

		return ret

# ex: noet ts=4 filetype=python
