from __future__ import absolute_import
from __future__ import unicode_literals

import collections
import re
import wbs

from wbs import ReportableError

class Inventory (object):

	def __init__ (self, context):

		self.context = context
		self.trace = context.trace

		self.world = {}

		self.classes = {}
		self.groups = {}
		self.resources = {}
		self.namespaces = {}

		self.group_children = collections.defaultdict (list)
		self.group_members = collections.defaultdict (list)

		self.resource_children = collections.defaultdict (list)

		self.class_groups = set ()

		self.load_world ()

	def load_world (self):

		world = {}

		self.all = {
			"HOME": self.context.home,
			"WORK": "%s/work" % self.context.home,
			"NAME": self.context.project_metadata ["project"] ["name"],
			"SHORT_NAME": self.context.project_metadata ["project"] ["short_name"],
			"SHORT_TITLE": self.context.project_metadata ["project"] ["short_title"],
			"CONNECTION": self.context.connection_name,
			"GRIDLINKER_HOME": self.context.gridlinker_home,
			"METADATA": self.context.project_metadata,
		}

		if "globals" in self.context.local_data:

			for prefix, data in self.context.local_data ["globals"].items ():

				self.all [prefix] = data

				if isinstance (data, dict):

					for name, value in data.items ():
						self.all [prefix + "_" + name] = value

		self.load_classes ()
		self.load_resources_1 ()
		self.load_resources_2 ()
		self.load_resources_3 ()
		self.load_resources_4 ()
		self.load_resources_5 ()

	def load_classes (self):

		class_list = self.context.local_data ["classes"].items ()

		for class_name, class_data in class_list:

			# check basics

			if not "identity" in class_data:

				raise Exception ()

			if class_data ["identity"] ["type"] != "class":

				raise Exception (
					"Class does not contain correct type: %s" % class_name)

			if class_name != class_data ["identity"] ["name"]:

				raise Exception (
					"Class does not contain correct name: %s" % class_name)

			# check for duplicates

			if class_name in self.world:

				raise Exception (
					"Class is duplicated: %s" % class_name)

			# fill in defaults

			class_data.setdefault ("class", {})
			class_data ["class"].setdefault ("groups", [])

			namespace = class_data ["class"] ["namespace"]

			# create class

			self.world [class_name] = class_data
			self.classes [class_name] = class_data

			self.namespaces.setdefault (namespace, [])

	def load_resources_1 (self):

		for resource_name, resource_data \
		in self.context.resources.get_all_list_quick ():

			resource_data = wbs.deep_copy (resource_data)

			# check basics

			if not "identity" in resource_data:
				raise Exception ()

			if resource_data ["identity"] ["type"] != "resource":

				raise Exception (
					"Invalid type '%s' for resource '%s'" % (
						resource_data ["identity"] ["type"],
						resource_name))

			# work out class

			class_name = resource_data ["identity"] ["class"]

			if not class_name in self.classes:

				raise Exception (
					"Invalid class %s for resource %s" % (
						class_name,
						resource_name))

			class_data = self.classes [class_name]

			# work out unique name

			unique_name = "%s/%s" % (
				class_data ["class"] ["namespace"],
				resource_data ["identity"] ["name"])

			if resource_name != unique_name:

				raise Exception (
					"Resource does not contain correct name: %s" % resource_name)

			namespace = class_data ["class"] ["namespace"]

			# check for duplicates

			if resource_name in self.world:

				raise Exception (
					"Resource is duplicated: %s" % resource_name)

			# add class data

			for prefix, data in class_data.items ():

				if prefix in [ "identity", "class" ]:
					continue

				if not prefix in resource_data:
					resource_data [prefix] = collections.OrderedDict ()

				for name, value in data.items ():

					if name not in resource_data [prefix]:

						resource_data [prefix] [name] = value

					elif value != "{{ None }}" \
					and value != resource_data [prefix] [name]:

						#raise Exception (
						#	"Specified %s.%s twice for %s" % (
						#	prefix,
						#	name,
						#	resource_name))

						pass

			# create expanded versions of keys

			for prefix, data in resource_data.items ():

				if not isinstance (data, dict):
					continue

				for name, value in data.items ():
					resource_data [prefix + "_" + name] = value

			# create resource

			self.world [resource_name] = resource_data
			self.resources [resource_name] = resource_data

			self.group_members [class_name].append (resource_name)
			self.namespaces [namespace].append (resource_name)

	def load_resources_2 (self):

		for resource_name, resource_data \
		in self.resources.items ():

			class_name = resource_data ["identity"] ["class"]
			class_data = self.classes [class_name]

			# set identity parent and grandparent

			if "parent" in resource_data ["identity"]:

				parent_name = "%s/%s" % (
					class_data ["class"] ["parent_namespace"],
					resource_data ["identity"] ["parent"])

				if not parent_name in self.resources:

					raise Exception (
						"Can't find parent of %s: %s" % (
							resource_name,
							parent_name))

				parent_data = self.resources [parent_name]

				self.resource_children [parent_name].append (resource_name)

				if "parent" in parent_data ["identity"]:

					resource_data ["identity"] ["grandparent"] = \
						parent_data ["identity"] ["parent"]

		# set children

		for resource_name, resource_data \
		in self.resources.items ():

			resource_data ["identity"] ["children"] = \
				self.resource_children [resource_name]

	def load_resources_3 (self):

		for resource_name, resource_data \
		in self.resources.items ():

			class_name = resource_data ["identity"] ["class"]
			class_data = self.classes [class_name]

			# resolve values where possible

			for prefix, data in resource_data.items ():

				if not isinstance (data, dict):
					continue

				for name, value in data.items ():

					resolved = (
						self.resolve_value_or_same (
							resource_name,
							value,
							""))

					resource_data [prefix] [name] = resolved
					resource_data [prefix + "_" + name] = resolved

	def load_resources_4 (self):

		for resource_name, resource_data \
		in self.resources.items ():

			class_name = resource_data ["identity"] ["class"]
			class_data = self.classes [class_name]

			if "parent" in resource_data ["identity"]:

				parent_name = "%s/%s" % (
					class_data ["class"] ["parent_namespace"],
					resource_data ["identity"] ["parent"])

				resource_data ["parent"] = "{{ hostvars ['%s'] }}" % (
					parent_name)

				if "grandparent" in resource_data ["identity"]:

					parent_data = self.resources [parent_name]

					parent_class_name = parent_data ["identity"] ["class"]
					parent_class_data = self.classes [parent_class_name]

					grandparent_name = "%s/%s" % (
						parent_class_data ["class"] ["parent_namespace"],
						parent_data ["identity"] ["parent"])

					resource_data ["grandparent"] = "{{ hostvars ['%s'] }}" % (
						grandparent_name)

			for reference in class_data ["class"].get ("references", []):

				if reference ["type"] == "resource":

					target_name = self.resolve_value_or_fail (
						resource_name,
						reference ["value"])

					if not target_name in self.resources:

						raise ReportableError (
							"inventory_referenced_resource_does_not_exist",
							resource_name = resource_name,
							referenced_resource_name = target_name,
							reference_name = reference ["name"])

					resource_data [reference ["name"]] = (
						"{{ hostvars ['%s'] }}" % (
							target_name))

				else:

					raise Exception ()

			for back_reference in class_data ["class"].get ("back_references", []):

				if back_reference ["type"] == "resource":

					namespace = back_reference ["namespace"]
					field = back_reference ["field"]

					section = back_reference ["section"]
					name = back_reference ["name"]

					values = []

					for other_resource_name in self.namespaces [namespace]:

						other_resource_data = self.resources [other_resource_name]

						if not field in other_resource_data:
							continue

						other_values = other_resource_data [field]

						if not isinstance (other_values, list):
							other_values = [ other_values ]

						if not resource_data ["identity"] ["name"] in other_values:
							continue

						values.append (other_resource_data ["identity"] ["name"])

					resource_data [section] [name] = values
					resource_data [section + "_" + name] = values

				else:

					raise Exception ()

			for back_reference in class_data ["class"].get ("back_references", []):

				if back_reference ["type"] == "resource":

					namespace = back_reference ["namespace"]
					field = back_reference ["field"]

					section = back_reference ["section"]
					name = back_reference ["name"]

					values = []

					for other_resource_name in self.namespaces [namespace]:

						other_resource_data = self.resources [other_resource_name]

						if not field in other_resource_data:
							continue

						other_values = other_resource_data [field]

						if not isinstance (other_values, list):
							other_values = [ other_values ]

						if not resource_data ["identity"] ["name"] in other_values:
							continue

						values.append (other_resource_data ["identity"] ["name"])

					resource_data [section] [name] = values
					resource_data [section + "_" + name] = values

				else:

					raise Exception ()

	def load_resources_5 (self):

		for resource_name, resource_data \
		in self.resources.items ():

			class_name = resource_data ["identity"] ["class"]
			class_data = self.classes [class_name]

			# groups

			for group_template in class_data ["class"] ["groups"]:

				group_name = (
					self.resolve_value_or_none (
						resource_name,
						group_template,
						""))

				if not group_name:
					continue

				if not group_name in self.class_groups:

					if group_name in self.world:
						raise Exception ()

					self.class_groups.add (group_name)

				self.group_members [group_name].append (resource_name)

	def add_group_class_type (self,
			item_friendly_name,
			item_short_name,
			item_data):

		item_name = item_data [item_short_name + "_name"]

		if item_short_name + "_group" in item_data:

			# add to group

			item_group = item_data [item_short_name + "_group"]

			if not item_group in all_groups:

				raise Exception (
					"%s %s has invalid group: %s" % (
						item_friendly_name,
						item_name,
						item_group))

			group_data = all_groups [item_group]

			all_groups [item_group] ["hosts"].append (item_name)

			# add to class

			group_class = group_data ["vars"] ["group_class"]

			if not group_class in all_groups:

				raise Exception ()

			class_data = all_groups [group_class]

			all_groups [group_class] ["hosts"].append (item_name)

			# add to type

			group_type = class_data ["vars"] ["class_type"]

			if not group_type in all_groups:

				raise Exception ()

			type_data = all_groups [group_type]

			all_groups [group_type] ["hosts"].append (item_name)

		elif item_short_name + "_class" in item_data:

			item_class = item_data [item_short_name + "_class"]
			class_data = all_groups [item_class]
			all_groups [item_class] ["hosts"].append (item_name)

			group_type = class_data ["vars"] ["class_type"]
			type_data = all_groups [group_type]
			all_groups [group_type] ["hosts"].append (item_name)

	def resolve_group (self, group_name, group_data):

		group_vars = group_data.get ("global", {})

		for prefix, data in group_data.items ():

			if prefix == "identity":
				continue

			group_vars [prefix] = data

		return group_vars

	def resolve_class (self, class_name, class_data):

		class_vars = class_data.get ("global", {})

		for prefix, data in class_data.items ():

			if prefix == "identity":
				continue

			class_vars [prefix] = data

		return class_vars

	def resolve_value_or_fail (self, resource_name, value):

		success, resolved = (
			self.resolve_value_real (
				resource_name,
				value,
				""))

		if not success:

			raise Exception (
				"Unable to resolve '%s' for resource '%s'" % (
					value,
					resource_name))

		return resolved

	def resolve_value_or_same (self, resource_name, value, indent):

		success, resolved = (
			self.resolve_value_real (
				resource_name,
				value,
				indent))

		if not success:
			return value

		return resolved

	def resolve_value_or_none (self, resource_name, value, indent):

		success, resolved = (
			self.resolve_value_real (
				resource_name,
				value,
				indent))

		if not success:
			return None

		return resolved

	def resolve_value_real (self, resource_name, value, indent):

		resource_data = self.resources [resource_name]

		if isinstance (value, list):

			ret = []

			for item in value:

				success, resolved = self.resolve_value_real (
					resource_name,
					item,
					indent)

				if not success:
					return False, None

				ret.append (resolved)

			return True, ret

		elif isinstance (value, dict):

			ret = collections.OrderedDict ()

			for key, item in value.items ():

				success, resolved = self.resolve_value_real (
					resource_name,
					item,
					indent)

				if not success:
					return False, None

				ret [key] = resolved

			return True, ret

		elif isinstance (value, str) \
		or isinstance (value, unicode):

			match = re.search (r"^\{\{\s*([^{}]*\S)\s*\}\}$", value)

			if match:

				return self.resolve_expression (
					resource_name,
					match.group (1),
					indent)

			else:

				ret = ""
				last_pos = 0

				for match in re.finditer (r"\{\{\s*(.*?)\s*\}\}", value):

					ret += value [last_pos : match.start ()]

					success, resolved = (
						self.resolve_expression (
							resource_name,
							match.group (1),
							indent))

					if not success:
						return False, None

					ret += str (resolved)

					last_pos = match.end ()

				ret += value [last_pos :]

				return True, ret

		else:

			return False, None

	def resolve_expression (self, resource_name, name, indent):

		if self.trace:

			print (
				"%sresolve_expression (%s, %s)" % (
					indent,
					resource_name,
					name))

		resource_data = self.resources [resource_name]

		success, tokens = self.tokenize (name)

		if not success:

			if self.trace:

				print (
					"%s  tokenize failed" % (
						indent))

			return False, None

		if self.trace:

			print (
				"%s  %s" % (
					indent,
					str (tokens)))

		token_index = 0

		success, token_index, value = (
			self.parse_expression (
				tokens,
				token_index,
				resource_name,
				indent + "  "))

		if not success:

			if self.trace:

				print (
					"%s  parse failed" % (
						indent))

			return False, None

		if token_index < len (tokens):

			if self.trace:

				print (
					"%s  only used %s/%s tokens" % (
						indent,
						token_index,
						len (tokens)))

			return False, None

		if self.trace:

			print (
				"%s  success: %s" % (
					indent,
					value))

		return True, value

	def parse_expression (self, tokens, token_index, resource_name, indent):

		success, token_index, value_type, value = (
			self.parse_simple (
				tokens,
				token_index,
				resource_name,
				indent))

		if not success:

			return False, None, None

		while token_index < len (tokens):

			if tokens [token_index] == ".":

				token_index += 1
				token = tokens [token_index]
				token_index += 1

				if value_type == "resource":

					success, value_type, value = (
						self.dereference_resource (
						value,
						token,
						indent))

					if success:
						continue

				elif value_type == "value":

					if token in value:

						value = value [token]

						continue

					elif str (token) in value:

						value = value [str (token)]

						continue

				else:

					raise Exception ()

				if self.trace:

					print (
						"%svalue not present: %s" % (
							indent,
							token))

				return False, None, None

			elif tokens [token_index] == "[":

				token_index += 1

				success, token_index, unresolved_value = (
					self.parse_expression (
						tokens,
						token_index,
						resource_name,
						indent + "  "))

				if not success:

					return False, None, None

				if tokens [token_index] != "]":

					return False, None, None

				token_index += 1

				success, resolved_value = (
					self.resolve_value_real (
						resource_name,
						unresolved_value,
						indent))

				if not success:

					return False, None, None

				if value_type == "resource":

					success, value_type, value = (
						self.dereference_resource (
						value,
						resolved_value,
						indent))

					if success:
						continue

				elif value_type == "value":

					if resolved_value in value:

						value = value [resolved_value]

						continue

					elif str (resolved_value) in value:

						value = value [str (resolved_value)]

						continue

				elif value_type == "hostvars":

					if resolved_value in self.resources:

						value_type = "resource"
						value = resolved_value

						continue

				if self.trace:

					print (
						"%svalue not present: %s" % (
							indent,
							token))

				return False, None, None

			else:

				break

		return True, token_index, value

	def parse_simple (self, tokens, token_index, resource_name, indent):

		token = tokens [token_index]

		resource_data = self.resources [resource_name]

		class_name = resource_data ["identity"] ["class"]
		class_data = self.classes [class_name]

		if token [0] == "'":

			string_value = (
				re.sub (
					r"\\(.)",
					lambda match: match.group (1),
					token [1 : -1]))

			return True, token_index + 1, "value", string_value

		if token == "hostvars":

			if self.trace:

				print (
					"%srecurse hostvars" % (
						indent))

			return True, token_index + 1, "hostvars", None

		if token in self.context.project_metadata ["project_data"]:

			if self.trace:

				print (
					"%sfound in project data: %s" % (
						indent,
						token))

			unresolved_value = (
				self.context.local_data [
					self.context.project_metadata ["project_data"] [token]])

			success, resolved_value = (
				self.resolve_value_real (
					resource_name,
					unresolved_value,
					indent + "  "))

			if not success:

				return False, None, None, None

			else:

				return True, token_index + 1, "value", resolved_value

		success, value_type, value = (
			self.dereference_resource (
				resource_name,
				token,
				indent))

		if success:

			return True, token_index + 1, value_type, value

		if self.trace:

			print (
				"%sunable to resolve: %s" % (
					indent,
					token))

		return False, token_index, None, None

	def dereference_resource (self, resource_name, token, indent):

		resource_data = self.resources [resource_name]

		class_name = resource_data ["identity"] ["class"]
		class_data = self.classes [class_name]

		for reference in class_data ["class"].get ("references", []):

			if token != reference ["name"]:
				continue

			if reference ["type"] == "resource":

				target_name = self.resolve_value_or_fail (
					resource_name,
					reference ["value"])

				if not target_name in self.resources:
					raise Exception ()

				target_data = self.resources [target_name]

				if self.trace:

					print (
						"%sfound class reference: %s" % (
							indent,
							token))

				return True, "resource", target_name

			else:

				raise Exception ()

		if token in resource_data:

			if self.trace:

				print (
					"%sfound in resource: %s" % (
						indent,
						token))

			return True, "value", resource_data [token]

		if token == "parent":

			parent_name = "%s/%s" % (
				class_data ["class"] ["parent_namespace"],
				resource_data ["identity"] ["parent"])

			parent_data = self.resources [parent_name]

			if self.trace:

				print (
					"%srecurse parent: %s" % (
						indent,
						parent_name))

			return True, "resource", parent_name

		if token in self.all:

			if self.trace:

				print (
					"%sfound in globals: %s" % (
						indent,
						token))

			unresolved_value = self.all [token]

			success, resolved_value = (
				self.resolve_value_real (
					resource_name,
					unresolved_value,
					indent))

			if success:

				return True, "value", resolved_value

			else:

				return False, None, None

		return False, None, None


	"""

		if name == "inventory_hostname":

			if self.trace:

				print (
					"  SUCCESS special variable: inventory_hostname")

			return True, resource_name

		if name == "None":

			if self.trace:

				print (
					"  SUCCESS special variable: None")

			return True, None

		class_name = resource_data ["identity"] ["class"]
		class_data = self.classes [class_name]

		parts = name.split (".")

		#if parts [0] in self.all:

		#	if self.trace:

		#		print (
		#			"  FAIL global variable: %s" % (
		#				parts [0]))

		#	return False, None

		if parts [0] == "grandparent":

			parent_name = "%s/%s" % (
				class_data ["class"] ["parent_namespace"],
				resource_data ["identity"] ["parent"])

			parent_data = self.resources [parent_name]

			parent_class_name = parent_data ["identity"] ["class"]
			parent_class_data = self.classes [parent_class_name]

			grandparent_name = "%s/%s" % (
				parent_class_data ["class"] ["parent_namespace"],
				parent_data ["identity"] ["parent"])

			grandparent_data = self.resources [grandparent_name]

			if self.trace:

				print (
					"  RECURSE resolved grandparent: %s" % (
						grandparent_name))

			return self.resolve_variable (
				grandparent_name,
				".".join (parts [1:]))

		match = re.search (r"\s*hostvars\s*\[\'([^']+)\'\]\s*", parts [0])

		if match:

			hostvars_name = match.group (1)
			hostvars_data = self.resources [hostvars_name]

			if self.trace:

				print (
					"  RECURSE resolved hostvars: %s" % (
						hostvars_name))

			return self.resolve_variable (
				hostvars_name,
				".".join (parts [1:]))

		for reference in class_data ["class"].get ("references", []):

			if not parts [0] == reference ["name"]:
				continue

			if reference ["type"] == "resource":

				target_name = self.resolve_value_or_fail (
					resource_name,
					reference ["value"])

				if not target_name in self.resources:
					raise Exception ()

				if self.trace:

					print (
						"  RECURSE resolved reference: %s" % (
							parts [0]))

				return self.resolve_variable (
					target_name,
					".".join (parts [1:]))

			else:

				raise Exception ()

		current = resource_data

		for index, part in enumerate (parts):

			if part in current:

				if self.trace:

					print (
						"  PARTIAL resolved part: %s" % (
							part))

				current = current [part]

			elif index == 0 and part in self.all:

				if self.trace:

					print (
						"  PARTIAL resolved global part: %s" % (
							part))

				current = self.resolve_value_real (
					resource_name,
					self.all [part])

			else:

				if self.trace:

					print (
						"  FAIL failed to resolve: %s" % (
							part))

				return False, None

		if isinstance (current, str):

			if self.trace:

				print (
					"  SUCCESS resolved string part: %s" % (
						part))

			return self.resolve_value_real (resource_name, current)

		if isinstance (current, unicode):

			if self.trace:

				print (
					"  SUCCESS resolved unicode part: %s" % (
						part))

			return self.resolve_value_real (resource_name, current)

		if isinstance (current, dict) \
		or isinstance (current, list):

			#return True, "{{ hostvars ['%s'].%s }}" % (
			#	resource_name,
			#	".".join (parts))

			return True, current

		if self.trace:

			print (
				"  FAIL unsupported type: %s" % (
					type (current)))

		return False, None

	"""

	tokenize_re = re.compile ("\s*((?:" + ")|(?:".join ([
		r"$",
		r"[][.]",
		r"[a-zA-Z][a-zA-Z0-9_]*",
		r"'(?:[^'\\]|\\\\|\\\')*'",
	]) + "))")

	def tokenize (self, string):

		ret = []
		position = 0

		while position < len (string):

			match = (
				Inventory.tokenize_re.match (
					string,
					position))

			if not match:
				return False, None

			ret.append (
				match.group (1))

			position = (
				match.end ())

		return True, ret

# ex: noet ts=4 filetype=yaml
