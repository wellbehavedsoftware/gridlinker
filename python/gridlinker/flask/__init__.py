from __future__ import absolute_import
from __future__ import unicode_literals

from gridlinker.flask import client
from gridlinker.flask.client import FlaskClient

from gridlinker.flask import collection
from gridlinker.flask.collection import GenericCollection

from gridlinker.flask import tools

def args (parser):
	tools.args (parser)

# ex: noet ts=4 filetype=yaml
