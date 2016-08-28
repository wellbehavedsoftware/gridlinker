from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import re

__all__ = [
	"FilterModule",
]

def substring_before (value, separator):

	return value.partition (separator) [0]

def substring_after (value, separator):

	return value.partition (separator) [3]

def starts_with (value, prefix):

	return value.startswith (prefix)

def join3 (values, prefix, separator, suffix):

	if not values:
		return ""

	full_separator = "".join ([
		suffix,
		separator,
		prefix,
	])

	return "".join ([
		prefix,
		full_separator.join (values),
		suffix,
	])

git_commit_id_regex = (
	re.compile (
		r"^[0-9a-f]{40}$"))

def git_version_shorten (value, length = 8):

	if git_commit_id_regex.match (value):
		return value [0 : length]

	else:
		return value

def prepend_list (items, string):

	return [
		string + item
		for item in items
	]

def append_list (items, string):

	return [
		item + string
		for item in items
	]

def replace_list (items, change_from, change_to):

	return [
		item.replace (
			change_from,
			change_to)
		for item
		in items
	]

class FilterModule (object):

    def filters (self):

        return {

			"substring_before": substring_before,
			"substring_after": substring_after,

			"prepend_list": prepend_list,
			"append_list": append_list,
			"replace_list": replace_list,

			"starts_with": starts_with,

			"join3": join3,

			"git_version_shorten": git_version_shorten,

		}

# ex: noet ts=4 filetype=python
