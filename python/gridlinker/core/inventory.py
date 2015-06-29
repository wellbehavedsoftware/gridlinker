from __future__ import absolute_import
from __future__ import unicode_literals

import collections
import re
import wbs

class Inventory (object):

	def __init__ (self, context):

		self.context = context

		self.world = {}

		self.classes = {}
		self.groups = {}
		self.resources = {}
		self.namespaces = {}

		self.children = collections.defaultdict (list)
		self.members = collections.defaultdict (list)

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

			# create resource

			self.world [resource_name] = resource_data
			self.resources [resource_name] = resource_data

			self.members [class_name].append (resource_name)
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

				parent_data = self.resources [parent_name]

				if "parent" in parent_data ["identity"]:

					resource_data ["identity"] ["grandparent"] = \
						parent_data ["identity"] ["parent"]

			# set children

			resource_data ["identity"] ["children"] = [
				other_name
				for other_name, other_data in self.resources.items ()
				if "parent" in other_data ["identity"]
				and other_data ["identity"] ["parent"] == resource_name
			]

	def load_resources_3 (self):

		for resource_name, resource_data \
		in self.resources.items ():

			class_name = resource_data ["identity"] ["class"]
			class_data = self.classes [class_name]

			# resolve values where possible

			for prefix, data in resource_data.items ():

				for name, value in data.items ():

					resolved = self.resolve_value_or_same (resource_name, value)

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

	def load_resources_5 (self):

		for resource_name, resource_data \
		in self.resources.items ():

			class_name = resource_data ["identity"] ["class"]
			class_data = self.classes [class_name]

			# groups

			for group_template in class_data ["class"] ["groups"]:

				group_name = self.resolve_value_or_none (resource_name, group_template)

				if not group_name:
					continue

				if not group_name in self.class_groups:

					if group_name in self.world:
						raise Exception ()

					self.class_groups.add (group_name)

				self.members [group_name].append (resource_name)

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

		success, resolved = self.resolve_value_real (resource_name, value)

		if not success:
			raise Exception ()

		return resolved

	def resolve_value_or_same (self, resource_name, value):

		success, resolved = self.resolve_value_real (resource_name, value)

		if not success:
			return value

		return resolved

	def resolve_value_or_none (self, resource_name, value):

		success, resolved = self.resolve_value_real (resource_name, value)

		if not success:
			return None

		return resolved

	def resolve_value_real (self, resource_name, value):

		resource_data = self.resources [resource_name]

		if isinstance (value, list):

			ret = []

			for item in value:

				success, resolved = self.resolve_value_real (
					resource_name,
					item)

				if not success:
					return False, None

				ret.append (resolved)

			return True, ret

		elif isinstance (value, dict):

			ret = collections.OrderedDict ()

			for key, item in value.items ():

				success, resolved = self.resolve_value_real (
					resource_name,
					item)

				if not success:
					return False, None

				ret [key] = item

			return True, ret

		elif isinstance (value, str) \
		or isinstance (value, unicode):

			match = re.search (r"^\{\{\s*([^{}]*\S)\s*\}\}$", value)

			if match:

				return self.resolve_variable (
					resource_name,
					match.group (1))

			else:

				ret = ""
				last_pos = 0

				for match in re.finditer (r"\{\{\s*(.*?)\s*\}\}", value):

					ret += value [last_pos : match.start ()]

					success, resolved = self.resolve_variable (
						resource_name,
						match.group (1))

					if not success:
						return False, None

					ret += str (resolved)

					last_pos = match.end ()

				ret += value [last_pos :]

				return True, ret

		else:

			return False, None

	def resolve_variable (self, resource_name, name):

		resource_data = self.resources [resource_name]

		if " " in name or "|" in name or "(" in name or "[" in name:
			return False, None

		if name == "inventory_hostname":
			return True, resource_name

		if name == "None":
			return True, None

		parts = name.split (".")

		if parts [0] in self.all:
			return False, None

		if parts [0] == "parent":

			class_name = resource_data ["identity"] ["class"]
			class_data = self.classes [class_name]

			parent_name = "%s/%s" % (
				class_data ["class"] ["parent_namespace"],
				resource_data ["identity"] ["parent"])

			parent_data = self.resources [parent_name]

			return self.resolve_variable (
				parent_name,
				".".join (parts [1:]))

		if parts [0] == "grandparent":

			parent_name = resource_data ["identity"] ["parent"]
			parent_data = self.resources [parent_name]

			grandparent_name = parent_data ["identity"] ["parent"]
			grandparent_data = self.resources [grandparent_name]

			return self.resolve_variable (
				grandparent_name,
				".".join (parts [1:]))

		current = resource_data

		for part in parts:

			if not part in current:
				return False, None

			current = current [part]

		if isinstance (current, str):
			return self.resolve_value_real (resource_name, current)

		if isinstance (current, unicode):
			return self.resolve_value_real (resource_name, current)

		return False, None

# ex: noet ts=4 filetype=yaml
