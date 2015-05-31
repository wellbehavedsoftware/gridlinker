from __future__ import absolute_import
from __future__ import unicode_literals

import collections
import json
import sys

def main (context, args):

	if args == []:

		raise Exception ()

	elif args [0] == "--list":

		do_list (context)

	elif args [0] == "--host":

		do_host (context, args [1])
	
	else:

		raise Exception ()

def load_classes (context, world):

	class_list = context.local_data ["classes"].items ()

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

		if class_name in world:

			raise Exception (
				"Class is duplicated: %s" % class_name)

		# create class

		world [class_name] = class_data

def load_groups (context, world):

	group_list = context.groups.get_all_list ()

	for group_name, group_data in group_list:

		# check basics

		if not "identity" in group_data:

			raise Exception (
				"Group does not have identity: %s" % group_name)

		if not "type" in group_data ["identity"]:

			raise Exception ()

		if group_data ["identity"] ["type"] != "group":

			raise Exception ()

		if group_name != group_data ["identity"] ["name"]:

			raise Exception (
				"Group does not contain correct name: %s" % class_group)

		# check for duplicates

		if group_name in world:

			raise Exception (
				"Group is duplicated: %s" % group_name)

		# create group

		world [group_name] = group_data

def load_resources (context, world):

	for resource_name, resource_data in context.resources.get_all_list ():

		# check basics

		if not "identity" in resource_data:

			raise Exception ()

		if resource_data ["identity"] ["type"] != "resource":

			raise Exception ()

		if resource_name != resource_data ["identity"] ["name"]:

			raise Exception (
				"Resource does not contain correct name: %s" % resource_name)

		# check for duplicates

		if resource_name in world:

			raise Exception (
				"Resource is duplicated: %s" % resource_name)

		# create resource

		world [resource_name] = resource_data

def add_group_class_type (context,
	all_groups,
	item_friendly_name,
	item_short_name,
	item_data
):

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

def resolve_group (group_name, group_data, world):

	group_vars = group_data.get ("global", {})

	for prefix, data in group_data.items ():

		if prefix == "identity":
			continue

		for name, value in data.items ():
			group_vars [prefix + "_" + name] = value

	return {
		"hosts": [
			entity_name
			for entity_name, entity_data in world.items ()
			if entity_data ["identity"] ["type"] == "resource"
			and "group" in entity_data ["identity"]
			and entity_data ["identity"] ["group"] == group_name
		],
		"vars": group_vars,
	}

def resolve_class (class_name, class_data, world):

	class_vars = class_data.get ("global", {})

	for prefix, data in class_data.items ():

		if prefix == "identity":
			continue

		for name, value in data.items ():
			class_vars [prefix + "_" + name] = value

	return {
		"hosts": [
			entity_name
			for entity_name, entity_data in world.items ()
			if entity_data ["identity"] ["type"] == "resource"
			and "class" in entity_data ["identity"]
			and entity_data ["identity"] ["class"] == class_name
		],
		"children": [
			entity_name
			for entity_name, entity_data in world.items ()
			if entity_data ["identity"] ["type"] == "group"
			and "class" in entity_data ["identity"]
			and entity_data ["identity"] ["class"] == class_name
		],
		"vars": class_vars,
	}

def resolve_resource (resource_name, resource_data, world):

	resource_vars = {}

	for prefix, data in resource_data.items ():

		for name, value in data.items ():
			resource_vars [prefix + "_" + name] = value

	if "parent" in resource_data ["identity"]:

		resource_vars ["parent"] = "{{ hostvars ['%s'] }}" % (
			resource_data ["identity"] ["parent"])

	elif "group" in resource_data ["identity"]:

		group_data = world [resource_data ["identity"] ["group"]]

		if "parent" in group_data ["identity"]:

			resource_vars ["parent"] = "{{ hostvars ['%s'] }}" % (
				group_data ["identity"] ["parent"])

	return resource_vars

def load_world (context):

	world = {}

	world ["all"] = {
		"identity": {
			"type": "group",
		},
		"global": {
			"HOME": context.home,
			"WORK": "%s/work" % context.home,
		},
	}

	load_classes (context, world)
	load_groups (context, world)

	load_resources (context, world)

	return {

		"groups": dict ([

			(entity_name, resolve_class (entity_name, entity_data, world))
			for entity_name, entity_data in world.items ()
			if entity_data ["identity"] ["type"] == "class"

		] + [

			(entity_name, resolve_group (entity_name, entity_data, world))
			for entity_name, entity_data in world.items ()
			if entity_data ["identity"] ["type"] == "group"

		]),

		"hosts": dict ([

			(entity_name, resolve_resource (entity_name, entity_data, world))
			for entity_name, entity_data in world.items ()
			if entity_data ["identity"] ["type"] == "resource"

		]),

	}

def do_list (context):

	output = {
		"_meta": {
			"hostvars": {},
		},
	}

	world = load_world (context)

	for group_name, group_data in world ["groups"].items ():
		output [group_name] = group_data
	
	for host_name, host_data in world ["hosts"].items ():
		output ["_meta"] ["hostvars"] [host_name] = host_data
	
	print_json (output)

def do_host (context, host_name):

	print_json (context.local_data ["hosts"] [host_name])

def print_json (data):

	print json.dumps (
		data,
		sort_keys = True,
		indent = 4,
		separators = (", ", ": "))

# ex: noet ts=4 filetype=yaml
