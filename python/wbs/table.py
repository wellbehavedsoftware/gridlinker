from __future__ import absolute_import
from __future__ import division
from __future__ import generators
from __future__ import nested_scopes
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import with_statement

class TableColumn (object):

	def __init__ (self, name, label):

		self.name = name
		self.label = label

def print_table (columns, rows, stream):

	# calculate column sizes

	column_sizes = {}

	for column in columns:

		max_size = len (column.label)

		for row in rows:

			value = row [column.name]
			length = len (value)

			if length > max_size:
				max_size = length

		column_sizes [column.name] = max_size

	# show headings

	stream.write ("\n ")

	for column in columns:

		column_size = column_sizes [column.name]

		stream.write (column.label.ljust (column_size + 1))

	stream.write ("\n")

	# show line

	stream.write ("-")

	for column in columns:

		column_size = column_sizes [column.name]

		stream.write ("-" * (column_size + 1))

	stream.write ("\n")

	# show data

	for row in rows:

		stream.write (" ")

		for column in columns:

			column_size = column_sizes [column.name]

			value = row [column.name]

			stream.write (value.ljust (column_size + 1))

		stream.write ("\n")

	stream.write ("\n")

# ex: noet ts=4 filetype=python
