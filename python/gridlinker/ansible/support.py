import os
import sys
import yaml

from gridlinker.core import GenericContext

existing_context = None

def get_context ():

	global existing_context

	if existing_context:
		return existing_context

	HOME = os.environ ["GRIDLINKER_PARENT_HOME"]
	CONNECTION = os.environ ["GRIDLINKER_CONNECTION"]

	with open ("%s/data/project" % HOME) as file_handle:
		METADATA = yaml.load (file_handle)

	existing_context = GenericContext (HOME, CONNECTION, METADATA)
	
	return existing_context

# ex: noet ts=4 filetype=python
