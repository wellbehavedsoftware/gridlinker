import etcd
import imp
import os
import sys

from ansible import utils

HOME = os.path.abspath (os.path.dirname (__file__) + "/../../..")

support_path = "%s/misc/plugin-support.py" % HOME

support = imp.load_source ("support", support_path)

class LookupModule (object):

	def __init__ (self, basedir = None, ** kwargs):

		self.basedir = basedir

		context = support.context ()

		self.client = context.client

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
