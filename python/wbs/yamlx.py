from __future__ import absolute_import
from __future__ import unicode_literals

import collections
import os
import sys
import yaml

# ordering code modified from here:
# https://gist.github.com/enaeseth/844388#file-yaml_ordered_dict-py

class OrderedDictYAMLLoader (yaml.Loader):

	def __init__ (self, * args, ** kwargs):

		yaml.Loader.__init__ (self, * args, ** kwargs)

		self.add_constructor (
			"tag:yaml.org,2002:map",
			type (self).construct_yaml_map)

		self.add_constructor (
			"tag:yaml.org,2002:omap",
			type (self).construct_yaml_map)

	def construct_yaml_map (self, node):

		data = collections.OrderedDict ()

		yield data

		value = self.construct_mapping (node)

		data.update (value)

	def construct_mapping (self, node, deep = False):

		if isinstance (node, yaml.MappingNode):

			self.flatten_mapping (node)

		else:

			raise yaml.constructor.ConstructorError (
				None,
				None,
				"expected a mapping node, but found %s" % node.id,
				node.start_mark)

		mapping = collections.OrderedDict ()

		for key_node, value_node in node.value:

			key = self.construct_object (key_node, deep = deep)

			try:
				hash (key)

			except TypeError as exc:

				raise yaml.constructor.ConstructorError (
					"while constructing a mapping",
					node.start_mark,
					"found unacceptable key (%s)" % exc,
					key_node.start_mark)

			value = self.construct_object (value_node, deep = deep)

			mapping [key] = value

		return mapping

def parse (string):

	return yaml.load (string, OrderedDictYAMLLoader)

def encode (schema, data):

	yaml = "---\n\n"

	yaml += "%s" % encode_real (schema, data, "", True)

	yaml += "\n\n# ex: et ts=2 filetype=yaml"

	return yaml

def encode_real (schema, data, indent, here):

	if isinstance (data, str) \
	or isinstance (data, unicode):
		return encode_str (schema, data, indent, here)

	if isinstance (data, dict):
		return encode_dict (schema, data, indent, here)

	if isinstance (data, list):
		return encode_list (schema, data, indent, here)

	raise Exception ("Don't know how to handle %s" % type (data))

def encode_str (schema, data, indent, here):

	return "\"%s\"" % data

def encode_list (schema, data, indent, here):

	if not data:
		return "[]"

	yaml = ""
	next_indent = indent + "  "

	for item in data:

		if not here:

			yaml += "\n"
			yaml += indent

		yaml += "- "
		yaml += encode_real (schema, item, next_indent, True)

		here = False

	return yaml

def encode_dict (schema, data, indent, here):

	if not data:
		return "{}"

	yaml = ""
	next_indent = indent + "  "

	done_keys = {}

	if schema:
		field_groups = schema.groups
	else:
		field_groups = []

	for group in field_groups:

		new_group = True

		for field in group.fields:

			if field.name in data:
				value = data [field.name]
			elif field.default is not None:
				value = field.default
			else:
				continue

			if not here:

				yaml += "\n"
				yaml += indent

				if new_group:

					yaml += "\n"
					yaml += indent

			yaml += field.name
			yaml += ": "
			yaml += encode_real (field.sub_schema, value, next_indent, False)

			done_keys [field.name] = True

			here = False
			new_group = False

	new_group = True

	for key in sorted (data.keys ()):

		if key in done_keys:
			continue;

		sys.stderr.write ("warning: unrecognised key: %s\n" % key)

		value = data [key]

		if not here:

			yaml += "\n"
			yaml += indent

			if new_group:

				yaml += "\n"
				yaml += indent

		yaml += key
		yaml += ": "
		yaml += encode_real (None, data [key], next_indent, False)

		here = False
		new_group = False

	return yaml + "\n"

def load_data (path):

	if os.path.isdir (path):

		ret = {}

		for child_name in os.listdir (path):

			child_path = path + "/" + child_name
			ret [child_name] = load_data (child_path)

		return ret

	elif os.path.isfile (path):

		with open (path) as file_handle:
			return parse (file_handle)

	else:

		raise Exception (
			"File or directory doesn't exist: %s" % (
				path))

# ex: noet ts=4 filetype=yaml
