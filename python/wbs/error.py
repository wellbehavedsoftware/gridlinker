from __future__ import absolute_import
from __future__ import unicode_literals

import sys
import textwrap

errors = dict ()

def register_error (name, ** kwargs):

	errors [name] = dict (** kwargs)

class ReportableError (BaseException):

	def __init__ (self, name, ** kwparams):

		if not name in errors:

			raise Exception (
				"Attempted to create invalid reportable error: %s" % (
					name))

		self.name = name
		self.short = errors [name] ["short"]
		self.long = errors [name] ["long"]
		self.params = kwparams

def error_exit (error):

	short_text = error.short.format (** error.params)
	long_text = error.long.format (** error.params)

	wrapper = textwrap.TextWrapper (
		replace_whitespace = True,
		drop_whitespace = True,
		width = 80)

	long_text = long_text.strip ()
	long_text = textwrap.dedent (long_text)
	long_text = wrapper.fill (long_text)

	sys.stderr.write (
		"\nERROR: %s\n\n%s\n\n" % (
			short_text,
			long_text))

	sys.exit (1)

# ex: noet ts=4 filetype=yaml
