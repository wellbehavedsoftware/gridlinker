from __future__ import absolute_import
from __future__ import unicode_literals

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

def load_types (context, all_groups):

	type_list = context.local_data ["types"].items ()

	for type_name, type_data in type_list:

		if not type_data:
			type_data = {}

		type_data.setdefault ("type_name", type_name)

		if type_name != type_data ["type_name"]:
			raise Exception ()

		type_data ["record_type"] = "type"

		all_groups [type_name] = {
			"children": [],
			"hosts": [],
			"vars": type_data,
		}

	# add to parents

	for type_name, type_data in type_list:

		if not "type_parent" in type_data:
			continue

		type_parent = type_data ["type_parent"]

		if not type_parent in all_groups:
			raise Exception (
				"Parent type of %s does not exist: %s" % (
					type_name,
					type_parent))

		all_groups [type_parent] ["children"].append (type_name)

def load_classes (context, all_groups):

	class_list = context.local_data ["classes"].items ()

	for class_name, class_data in class_list:

		# check "class_name"

		class_data.setdefault ("class_name", class_name)

		if class_name != class_data ["class_name"]:
			raise Exception ()

		# check for duplicates

		if class_name in all_groups:
			raise Exception ()

		# check "class_type"

		if not "class_type" in class_data:

			raise Exception (
				"Class %s has no type" % (
					class_name))

		class_type = class_data ["class_type"]

		if not class_type in all_groups:

			raise Exception (
				"Class %s has unrecognised type: %s" % (
					class_name,
					class_type))

		# create class

		class_data ["record_type"] = "class"

		all_groups [class_name] = {
			"children": [],
			"hosts": [],
			"vars": class_data,
		}

	# add to parents

	for class_name, class_data in class_list:

		if not "class_parent" in class_data:
			continue

		class_parent = class_data ["class_parent"]

		if not class_parent in all_groups:
			raise Exception (
				"Parent class of %s does not exist: %s" % (
					class_name,
					class_parent))

		all_groups [class_parent] ["children"].append (class_name)

def load_groups (context, all_groups):

	group_list = context.groups.get_all_list ()

	for group_name, group_data in group_list:

		# check "group_name"

		group_data.setdefault ("group_name", group_name)

		if group_name != group_data ["group_name"]:
			raise Exception (
				"Group name mismatch: %s / %s" % (
					group_name,
					group_data ["group_name"]))

		# check for duplicates

		if group_name in all_groups:

			raise Exception (
				"Duplicate group name: %s" % (
					group_name))

		# check "group_class"

		if not "group_class" in group_data:

			raise Exception (
				"Group %s has no class" % (
					group_name))

		group_class = group_data ["group_class"]

		if not group_class in all_groups:

			raise Exception (
				"Group %s has unrecognised class: %s" % (
					group_name,
					group_class))

		# create group

		group_data ["record_type"] = "group"

		all_groups [group_name] = {
			"children": [],
			"hosts": [],
			"vars": group_data,
		}

	# add to parents

	for group_name, group_data in group_list:

		if not "group_parent" in group_data:
			continue

		group_parent = group_data ["group_parent"]

		if not group_parent in all_groups:

			raise Exception (
				"Group %s has unrecognised parent: %s" % (
					group_name,
					group_parent))

		all_groups [group_parent] ["children"].append (group_name)

def load_hosts (context, all_groups, all_hosts):

	for host_name, host_data in context.hosts.get_all_list ():

		host_data ["collection_name"] = "hosts"

		if host_name in all_groups:
			raise Exception ()

		if host_name in all_hosts:
			raise Exception ()

		all_hosts [host_name] = host_data

		add_group_class_type (context, all_groups, "host", "host", host_data)

def load_amazon_accounts (context, all_groups, all_hosts):

	for account_name, account_data in context.amazon_accounts.get_all_list ():

		account_data ["collection_name"] = "amazon_accounts"

		if account_name in all_groups:
			raise Exception (
				"Duplicated name: %s" % account_name)

		if account_name in all_hosts:
			raise Exception (
				"Duplicated name: %s" % account_name)

		all_hosts [account_name] = account_data

		add_group_class_type (context, all_groups, "amazon account", "account", account_data)

def load_amazon_vpcs (context, all_groups, all_hosts):

	for vpc_name, vpc_data in context.amazon_vpcs.get_all_list ():

		vpc_data ["collection_name"] = "amazon_vpcs"

		if vpc_name in all_groups:
			raise Exception ()

		if vpc_name in all_hosts:
			raise Exception ()

		all_hosts [vpc_name] = vpc_data

		add_group_class_type (context, all_groups, "amazon vpc", "vpc", vpc_data)

def load_amazon_balancers (context, all_groups, all_hosts):

	for balancer_name, balancer_data in context.amazon_balancers.get_all_list ():

		balancer_data ["collection_name"] = "amazon_balancers"

		if balancer_name in all_groups:
			raise Exception ()

		if balancer_name in all_hosts:
			raise Exception ()

		all_hosts [balancer_name] = balancer_data

		add_group_class_type (context, all_groups, "amazon balancer", "balancer", balancer_data)

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

def load_all (context):

	all_groups = {}
	all_hosts = {}

	load_types (context, all_groups)
	load_classes (context, all_groups)
	load_groups (context, all_groups)

	load_hosts (context, all_groups, all_hosts)
	load_amazon_accounts (context, all_groups, all_hosts)
	load_amazon_vpcs (context, all_groups, all_hosts)
	load_amazon_balancers (context, all_groups, all_hosts)

	# special case for group "all"

	if not "all" in all_groups:

		all_groups ["all"] = {
			"children": [],
			"hosts": [],
			"vars": {},
		}

	all_groups ["all"] ["vars"] ["HOME"] = context.home
	all_groups ["all"] ["vars"] ["WORK"] = "%s/work" % context.home

	all_groups ["all"] ["vars"].update (context.local_data ["defaults"])
	all_groups ["all"] ["vars"].update (context.overrides_data)

	all_groups ["all"] ["vars"] ["amazon_accounts"] = \
		context.amazon_accounts.get_all_dictionary ()

	all_groups ["all"] ["vars"] ["amazon_vpcs"] = \
		context.amazon_vpcs.get_all_dictionary ()

	return {
		"groups": all_groups,
		"hosts": all_hosts,
	}


def do_list (context):

	output = {}

	data = load_all (context)

	for key, value in data ["groups"].items ():
		output [key] = value

	output ["_meta"] = {
		"hostvars": data ["hosts"],
	}

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
