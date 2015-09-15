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

def format_text (text, params = dict ()):

	wrapper = textwrap.TextWrapper (
		replace_whitespace = True,
		drop_whitespace = True,
		width = 80)

	text = text.format (** params)
	text = textwrap.dedent (text)
	text = text.strip ()
	text = wrapper.fill (text)

	return text

def error_exit (error):

	long_text = format_text (error.long, error.params)

	short_text = format_text (error.short, error.params)
	short_text = "ERROR: %s" % short_text
	short_text = format_text (short_text)

	sys.stderr.write (
		"\n%s\n\n%s\n\n" % (
			short_text,
			long_text))

	sys.exit (1)

# ex: noet ts=4 filetype=yaml
