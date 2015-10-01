from __future__ import absolute_import
from __future__ import unicode_literals

import httplib
import itertools
import json
import os
import random
import re
import ssl
import time
import urllib

from wbs import yamlx

class EtcdClient:

	def __init__ (
		self,
		servers = [ "localhost" ],
		port = 2379,
		secure = False,
		client_ca_cert = None,
		client_cert = None,
		client_key = None,
		prefix = "",
	):

		self.servers = servers
		self.port = port
		self.secure = secure
		self.client_ca_cert = client_ca_cert
		self.client_cert = client_cert
		self.client_key = client_key
		self.prefix = prefix

		self.connection = None
		self.pid = None

		random.shuffle (self.servers)

		if self.secure:

			self.server_url = "https://%s:%s" % (self.servers [0], self.port)

			self.ssl_context = ssl.SSLContext (
				ssl.PROTOCOL_TLSv1_2)

			self.ssl_context.verify_mode = ssl.CERT_REQUIRED
			self.ssl_context.check_hostname = False

			self.ssl_context.load_verify_locations (
				cafile = self.client_ca_cert)

		else:

			self.server_url = "http://%s:%s" % (self.servers [0], self.port)

	def get_connection (self):

		if os.getpid () == self.pid and self.connection:
			return self.connection

		if self.secure:

			connection = httplib.HTTPSConnection (
				host = self.servers [0],
				port = self.port,
				key_file = self.client_key,
				cert_file = self.client_cert,
				context = self.ssl_context,
				timeout = 4)

			connection.connect ()

			peer_certificate = connection.sock.getpeercert ()
			peer_alt_names = peer_certificate ["subjectAltName"]

			# check if the server is an ip address

			if re.match (
				r"^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$",
				self.servers [0]):

				# match ip addresses with custom code

				if not self.servers [0] in [
					alt_value
					for alt_type, alt_value in peer_alt_names
					if alt_type == 'IP Address'
				]:

					raise Exception ("".join ([
						"Etcd server certificate failed to match IP address ",
						"'%s'" % self.servers [0],
					]))

			else:

				# match hostnames using python implementation

				ssl.match_hostname (
					peer_certificate,
					self.servers [0])

			self.connection = connection

		else:

			connection = httplib.HTTPConnection (
				host = self.servers [0],
				port = self.port)

			connection.connect ()

			self.connection = connection

		self.pid = os.getpid ()

		return self.connection

	def key_url (self, key):

		url_string = u"/v2/keys%s%s" % (
			self.prefix,
			key)

		return url_string

	def exists (self, key):

		result, _ = self.make_request (
			method = "GET",
			url = self.key_url (key),
			accept_response = [ 200, 404 ])

		if result == 200:
			return True

		if result == 404:
			return False

		raise Exception ()

	def get_raw (self, key):

		result, data = self.make_request (
			method = "GET",
			url = self.key_url (key),
			accept_response = [ 200, 404 ])

		if result == 404:

			raise LookupError (
				"No such key: %s" % key)

		return data ["node"] ["value"]

	def get_raw_or_none (self, key):

		result, data = self.make_request (
			method = "GET",
			url = self.key_url (key),
			accept_response = [ 200, 404 ])

		if result == 404:

			return None

		return data ["node"] ["value"]

	def set_raw (self, key, value):

		self.make_request (
			method = "PUT",
			url = self.key_url (key),
			payload_data = {
				"value": value,
			})

	def make_request (self, ** kwargs):

		for _ in itertools.repeat (5):

			try:

				return self.make_request_real (** kwargs)

			except (httplib.HTTPException, IOError):

				if self.connection:

					self.connection.close ()
					self.connection = None

				random.shuffle (self.servers)

				time.sleep (1)

		return self.make_request_real (** kwargs)

	def make_request_real (self,
		method,
		url,
		query_data = {},
		payload_data = {},
		accept_response = [ 200, 201 ]):

		# prepare query

		query_string = urllib.urlencode (query_data)

		if query_string:
			url += "&" if "?" in url else "?"
			url += query_string

		# prepare payload

		payload_string = urllib.urlencode (payload_data)
		payload_bytes = payload_string.encode ("utf-8")

		# get connection

		connection = self.get_connection ()

		# send request

		connection.putrequest (method, url)

		if payload_string:

			connection.putheader (
				"Content-Length",
				len (payload_bytes))

			connection.putheader (
				"Content-Type",
				"application/x-www-form-urlencoded")

		connection.endheaders ()

		if payload_data:
			connection.send (payload_bytes)

		# read response

		response = connection.getresponse ()

		response_bytes = response.read ()

		# check response

		if not response.status in accept_response:

			raise Exception (
				"Error %s: %s" % (
					response.status,
					response.reason))

		# decode response

		if response.getheader ("Content-Type") == "application/json":

			return (
				response.status,
				json.loads (response_bytes.decode ("utf-8")),
			)

		else:

			return (
				response.status,
				None,
			)

	def update_raw (self, key, old_value, new_value):

		self.make_request (
			method = "PUT",
			url = self.key_url (key),
			payload_data = {
				"prevValue": old_value,
				"value": new_value,
			},
			accept_response = [ 200 ])

	def create_raw (self, key, value):

		status, data = self.make_request (
			method = "PUT",
			url = self.key_url (key),
			payload_data = {
				"value": value,
				"prevExist": False,
			},
			accept_response = [ 201, 412 ])

		if status == 412:

			raise ValueError (
				"Key already exists: %s" % key)

	def get_list (self, key):

		nodes = dict (self.get_tree (key))

		return [
			nodes ["/%s" % index]
			for index in xrange (0, len (nodes))
		]

	def get_tree (self, key):

		status, data = self.make_request (
			method = "GET",
			url = self.key_url (key),
			query_data = {
				"recursive": "true",
			},
			accept_response = [ 200, 201, 404 ])

		if status == 404:
			return []

		return self.walk_tree (key, data ["node"])

	def walk_tree (self, prefix, node):

		if "value" in node:

			relative_key = node ["key"] [len (self.prefix) + len (prefix):]

			return [ (relative_key, node ["value"]) ]

		elif "nodes" in node:

			return [
				item for sub_list in [
					self.walk_tree (prefix, child_node)
					for child_node in node ["nodes"]
				] for item in sub_list
			]

		else:

			return []

	def rm (self, key):

		self.make_request (
			method = "DELETE",
			url = self.key_url (key),
			accept_response = [ 200 ])

	def rm_raw (self, key, value):

		self.make_request (
			method = "DELETE",
			url = self.key_url (key),
			query_data = {
				"prevValue": value,
			},
			accept_response = [ 200 ])

	def rm_recursive (self, key):

		self.make_request (
			method = "DELETE",
			url = self.key_url (key),
			query_data = {
				"recursive": "true",
			},
			accept_response = [ 200 ])

	def rmdir (self, key):

		self.make_request (
			method = "DELETE",
			url = self.key_url (key),
			query_data = {
				"dir": "true",
			},
			accept_response = [ 200 ])

	def mkdir_queue (self, key):

		status, data = self.make_request (
			method = "POST",
			url = self.key_url (key),
			query_data = {
				"dir": "true",
			},
			accept_response = [ 201 ])

		return (
			data ["node"] ["key"] [len (self.prefix) : ],
			data ["node"] ["createdIndex"],
		)

	def get_yaml (self, key):

		value_yaml = self.get_raw (key)
		value = yamlx.parse (value_yaml)

		return value

	def set_yaml (self, key, value, schema = None):

		value_yaml = yamlx.encode (schema, value)

		self.set_raw (key, value_yaml)

	def ls (self, key):

		status, data = self.make_request (
			method = "GET",
			url = self.key_url (key),
			accept_response = [ 200 ])

		if not "nodes" in data ["node"]:
			raise Exception ()

		prefix_length = len (self.prefix) + len (key)

		return [
			node ["key"] [prefix_length + 1 : ]
			for node in data ["node"] ["nodes"]
		]

def args (sub_parsers):

	pass

# ex: noet ts=4 filetype=yaml

