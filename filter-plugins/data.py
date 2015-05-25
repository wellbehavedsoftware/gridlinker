from __future__ import absolute_import

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

class FilterModule (object):

    def filters (self):

        return {

			"flatten_hash": flatten_hash,

		}
