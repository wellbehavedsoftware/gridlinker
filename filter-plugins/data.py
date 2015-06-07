from __future__ import absolute_import
from __future__ import unicode_literals

import itertools

def flatten_hash (values, * inner_names):

	ret = []

	for outer_key, outer_value in values.items ():

		for inner_items in itertools.product (* [
			outer_value [inner_name]
			for inner_name in inner_names
		]):

			item = {
				"outer": {
					"key": outer_key,
					"value": outer_value,
				},
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

class FilterModule (object):

    def filters (self):

        return {

			"flatten_hash": flatten_hash,
			"list_to_map": list_to_map,
			"dict_map": dict_map,

		}
