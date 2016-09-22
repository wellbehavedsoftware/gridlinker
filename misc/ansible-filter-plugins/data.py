from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import itertools
import re
import types

__all__ = [
	"FilterModule",
]

def flatten_hash (values, * inner_names):

	ret = []

	if isinstance (values, list) \
	or isinstance (values, types.GeneratorType):

		outer_list = [
			(item, item)
			for item in values
		]

	elif isinstance (values, dict):

		outer_list = [
			({ "key": outer_key, "value": outer_value }, outer_value)
			for outer_key, outer_value in values.items ()
		]

	else:

		raise Exception (
			"Don't know how to flatten a %s" % (
				type (values).__name__))

	for outer_item, outer_value in outer_list:

		for inner_items in itertools.product (* [
			outer_value [inner_name]
			for inner_name in inner_names
			if inner_name in outer_value
		]):

			if len (inner_items) < len (inner_names):
				continue

			item = {
				"outer": outer_item,
			}

			for index, inner_name in enumerate (inner_names):

				inner_item = inner_items [index]
				inner_collection = outer_value [inner_name]

				if isinstance (inner_collection, list):

					item [inner_name] = inner_item

				if isinstance (inner_collection, dict):

					item [inner_name] = {
						"key": inner_item,
						"value": inner_collection [inner_item],
					}

			ret.append (item)

	return ret

def property_get (value, path):

	if "." in path:

		first, rest = path.split (".", 1)
		return property_get (value [first], rest)

	else:

		return value [path]

def list_to_map (items, key_name, value_name):

	return dict ([
		(property_get (item, key_name), property_get (item, value_name))
		for item in items
	])

def dict_map (keys, mapping):

	return [
		mapping [key]
		for key in keys
	]

def index_by (items, index_key):

	return dict ([
		(item [index_key], item)
		for item
		in items
	])

def flatten_list (lists):

	return [
		item
		for list in lists
		for item in list
	]

def keys (item):

	return item.keys ();

def values (source):

	return source.values ()

def items (item):

	return item.items ();

def bytes (source):

	units = {
		"": 1,
		"B": 1,
		"KB": 1000,
		"MB": 1000 * 1000,
		"GB": 1000 * 1000 * 1000,
		"TB": 1000 * 1000 * 1000 * 1000,
		"KiB": 1024,
		"MiB": 1024 * 1024,
		"GiB": 1024 * 1024 * 1024,
		"TiB": 1024 * 1024 * 1024 * 1024,
	}

	match = (
		re.match (
			r"^\s*([0-9]+)\s*(%s)?\s*$" % (
				"|".join (units.keys ())),
			source))

	if not match:

		raise Exception (
			"Cannot convert '%s' to bytes'" % (
				source))

	size = int (match.group (1))
	unit = match.group (2)

	scale = units [unit]

	return size * scale

def to_dict (items):

	return dict (items)

class FilterModule (object):

    def filters (self):

        return {

			"flatten_hash": flatten_hash,
			"flatten_list": flatten_list,
			"list_to_map": list_to_map,
			"dict_map": dict_map,
			"index_by": index_by,

			"keys": keys,
			"values": values,
			"items": items,
			"to_dict": to_dict,

			"bytes": bytes,

		}

# ex: noet ts=4 filetype=python
