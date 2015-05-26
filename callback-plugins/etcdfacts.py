import imp
import os

HOME = os.path.abspath (os.path.dirname (__file__) + "/../../..")
support_path = "%s/misc/plugin-support.py" % HOME
support = imp.load_source ("support", support_path)
context = support.context ()

class CallbackModule (object):

	def __init__ (self):
		self.count = 0

	def runner_on_ok (self, record_name, result):

		if result ["invocation"] ["module_name"] != "set_fact":
			return

		found_records = [
			(collection, collection.get (record_name))
			for collection in context.collections
			if collection.exists (record_name)
		]

		if not found_records:
			raise Exception ("Not found: " + record_name)

		if len (found_records) > 1:
			raise Exception ("Found multiple")

		collection, record_data = found_records [0]

		for key, value in result ["ansible_facts"].items ():
			record_data [key] = value

		collection.set (record_name, record_data)
