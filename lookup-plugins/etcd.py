from __future__ import absolute_import

import os

from ansible import utils

support = __import__ (os.environ ["WBS_DEVOPS_TOOLS_SUPPORT"]).support

class LookupModule (object):

	def __init__ (self, basedir = None, ** kwargs):

		self.basedir = basedir

		self.client = support.context.client

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
