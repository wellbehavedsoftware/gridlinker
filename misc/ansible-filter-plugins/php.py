from __future__ import absolute_import
from __future__ import unicode_literals

import re

php_string_replacements = dict ({
	"\n": "\\n",
	"\r": "\\r",
	"\t": "\\t",
	"\v": "\\v",
	"\x1b": "\\e",
	"\x14": "\\f",
	"\\": "\\\\",
	"$": "\\$",
})

def php_escape (value):

	return re.sub (
		r"[\n\r\t\v\x1b\x14\\$]",
		lambda (match): php_string_replacements [match.group (0)],
		value)

class FilterModule (object):

    def filters (self):

        return {

			"php_escape": php_escape,

		}

# ex: noet ts=4 filetype=python
