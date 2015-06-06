from __future__ import absolute_import
from __future__ import unicode_literals

import importlib
import os

class CallbackModule (object):

	def __init__ (self):

		self.support = importlib.import_module (os.environ ["GRIDLINKER_SUPPORT"]).support
		self.context = self.support.get_context ()

	def runner_on_ok (self, record_name, result):

		if not result ["invocation"] ["module_name"] in [
			"set_fact",
			"set_fact_dynamic",
		]:
			return

		self.store_facts (record_name, result ["ansible_facts"])

	def __setattr__ (self, key, value):

		self.__dict__ [key] = value

	def store_facts (self, record_name, facts):

		found_records = []

		for collection in self.context.collections:

			if not collection.exists (record_name):
				continue

			found_records.append ((
				collection,
				collection.get (record_name),
			))

		if not found_records:
			raise Exception ("Not found: " + record_name)

		if len (found_records) > 1:
			raise Exception ("Found multiple")

		collection, record_data = found_records [0]

		for section_key, value in facts.items ():

			if not "." in section_key:
				continue

			section, key = section_key.split (".")

			if not section in record_data:
				record_data [section] = {}

			record_data [section] [key] = value

		collection.set (record_name, record_data)
