from __future__ import absolute_import
from __future__ import unicode_literals

import collections
import json
import re
import sys
import wbs

def main (context, args):

	inventory = Inventory (context)

	if args == []:

		raise Exception ()

	elif args [0] == "--list":

		inventory.do_list ()

	elif args [0] == "--host":

		inventory.do_host (args [1])

	else:

		raise Exception ()

class Inventory (object):

	def __init__ (self, context):

		self.context = context

		self.world = {}

		self.classes = {}
		self.groups = {}
		self.resources = {}

		self.children = collections.defaultdict (list)
		self.members = collections.defaultdict (list)

		self.class_groups = set ()

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

			# create class

			self.world [class_name] = class_data
			self.classes [class_name] = class_data

	def load_resources_1 (self):

		for resource_name, resource_data \
		in self.context.resources.get_all_list_quick ():

			resource_data = wbs.deep_copy (resource_data)

			# check basics

			if not "identity" in resource_data:
				raise Exception ()

			if resource_data ["identity"] ["type"] != "resource":
				raise Exception ()

			# work out class

			class_name = resource_data ["identity"] ["class"]

			if not class_name in self.classes:

				raise Exception (
					"Invalid class %s for resource %s" % (
						class_name,
						resource_name))

			class_data = self.classes [class_name]

			# work out unique name

			if class_data ["class"] ["scope"] == "global":

				unique_name = resource_data ["identity"] ["name"]

			elif class_data ["class"] ["scope"] == "class":

				unique_name = "%s/%s" % (
					class_name,
					resource_data ["identity"] ["name"])

			else:

				raise Exception ()

			if resource_name != unique_name:

				raise Exception (
					"Resource does not contain correct name: %s" % resource_name)

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

					if name in resource_data [prefix]:

						raise Exception (
							"Specified %s.%s twice for %s" % (
							prefix,
							name,
							resource_name))

					resource_data [prefix] [name] = value

			# create resource

			self.world [resource_name] = resource_data
			self.resources [resource_name] = resource_data

			self.members [class_name].append (resource_name)

	def load_resources_2 (self):

		for resource_name, resource_data \
		in self.resources.items ():

			class_name = resource_data ["identity"] ["class"]
			class_data = self.classes [class_name]

			# set identity parent and grandparent

			if "parent" in resource_data ["identity"]:

				parent_name = resource_data ["identity"] ["parent"]
				parent_data = self.resources [parent_name]

				if "parent" in parent_data ["identity"]:

					grandparent_name = parent_data ["identity"] ["parent"]

					resource_data ["identity"] ["grandparent"] = \
						grandparent_name

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

					resolved = self.resolve_value (
						resource_name,
						resource_data,
						value)

					resource_data [prefix] [name] = resolved
					resource_data [prefix + "_" + name] = resolved

	def load_resources_4 (self):

		for resource_name, resource_data \
		in self.resources.items ():

			class_name = resource_data ["identity"] ["class"]
			class_data = self.classes [class_name]

			# set parent and grandparent

			if "parent" in resource_data ["identity"]:

				resource_data ["parent"] = "{{ hostvars ['%s'] }}" % (
					resource_data ["identity"] ["parent"])

			if "grandparent" in resource_data ["identity"]:

				resource_data ["grandparent"] = "{{ hostvars ['%s'] }}" % (
					resource_data ["identity"] ["grandparent"])

	def load_resources_5 (self):

		for resource_name, resource_data \
		in self.resources.items ():

			class_name = resource_data ["identity"] ["class"]
			class_data = self.classes [class_name]

			# groups

			for group_template in class_data ["class"] ["groups"]:

				group_name = self.resolve_value (
					resource_name,
					resource_data, 				
					group_template)

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

	def resolve_value (self, resource_name, combined_data, value):

		if isinstance (value, list):

			return [
				self.resolve_value (resource_name, combined_data, item)
				for item in value
			]

		elif isinstance (value, dict):

			return collections.OrderedDict ([
				(key, self.resolve_value (resource_name, combined_data, item))
				for key, item in value.items ()
			])

		else:

			return re.sub (

				r"\{\{\s*(.*?)\s*\}\}",

				lambda match:

					self.resolve_variable (
						resource_name,
						combined_data,
						match.group (1),
					) or "{{ %s }}" % match.group (1),

				str (value))

	def resolve_variable (self, resource_name, combined_data, name):

		if " " in name or "|" in name or "(" in name or "[" in name:
			return None

		if name == "inventory_hostname":
			return resource_name

		parts = name.split (".")

		if parts [0] in self.all:
			return None

		if parts [0] == "parent":

			parent_name = combined_data ["identity"] ["parent"]
			parent_data = self.resources [parent_name]

			return self.resolve_variable (
				parent_name,
				parent_data,
				".".join (parts [1:]))

		if parts [0] == "grandparent":

			parent_name = combined_data ["identity"] ["parent"]
			parent_data = self.resources [parent_name]

			grandparent_name = parent_data ["identity"] ["parent"]
			grandparent_data = self.resources [grandparent_name]

			return self.resolve_variable (
				grandparent_name,
				grandparent_data,
				".".join (parts [1:]))

		current = combined_data

		for part in parts:

			if not part in current:
				return None

			current = current [part]

		if isinstance (current, str):
			return current

		if isinstance (current, unicode):
			return current

		return None

	def load_world (self):

		world = {}

		self.all = {
			"HOME": self.context.home,
			"WORK": "%s/work" % self.context.home,
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

	def do_list (self):

		output = {
			"_meta": {
				"hostvars": {},
			},
		}

		self.load_world ()

		output ["all"] = {
			"vars": self.all,
		}

		for class_name, class_data in self.classes.items ():

			output [class_name] = {
				"children": self.children [class_name],
				"hosts": self.members [class_name],
			}

		for group_name, group_data in self.groups.items ():

			output [group_name] = {
				"vars": group_data,
				"hosts": self.members [group_name],
			}

		for resource_name, resource_data in self.resources.items ():

			output ["_meta"] ["hostvars"] [resource_name] = \
				self.resources [resource_name]

		for key, value in self.context.project_metadata ["data"].items ():
			output ["all"] ["vars"] [key] = self.context.local_data [value]

		for key, value in self.context.project_metadata ["resource_data"].items ():

			if value in self.classes:

				class_name = value

				output ["all"] ["vars"] [key] = dict ([
					(
						self.resources [resource_name] ["identity"] ["name"],
						self.resources [resource_name],
					)
					for resource_name in self.members [class_name]
				])

			else:

				raise Exception ()

		for group_name in self.class_groups:

			output [group_name] = {
				"hosts": self.members [group_name],
			}

		print_json (output)

	def do_host (self, host_name):

		print_json (self.local_data ["hosts"] [host_name])

def print_json (data):

	print json.dumps (
		data,
		sort_keys = True,
		indent = 4,
		separators = (", ", ": "))

# ex: noet ts=4 filetype=yaml
