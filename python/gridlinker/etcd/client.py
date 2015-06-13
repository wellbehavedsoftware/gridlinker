from __future__ import absolute_import
from __future__ import unicode_literals

import httplib
import ipaddress
import json
import os
import ssl
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

		self.pid = None

	def get_connection (self):

		if os.getpid () != self.pid:

			if self.secure:

				connection = httplib.HTTPSConnection (
					host = self.servers [0],
					port = self.port,
					key_file = self.client_key,
					cert_file = self.client_cert,
					context = self.ssl_context)

				connection.connect ()

				peer_certificate = connection.sock.getpeercert ()
				peer_alt_names = peer_certificate ["subjectAltName"]

				# check if the server is an ip address

				try:

					ipaddress.ip_address (
						unicode (self.servers [0].encode ("utf-8")))

					is_ip_address = True

				except ValueError:

					is_ip_address = False

				if is_ip_address:

					# match ip addresses with custom code

					if not self.servers [0] in [
						alt_value
						for alt_type, alt_value in peer_alt_names
						if alt_type == 'IP Address'
					]:

						raise Exception ()

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

	def set_raw (self, key, value):

		self.make_request (
			method = "PUT",
			url = self.key_url (key),
			payload_data = {
				"value": value,
			})

	def make_request (self, method, url,
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

		payload = {
			"prevValue": old_value,
			"value": new_value,
		}

		response = self.http ().request_encode_body (
			"PUT",
			self.key_url (key),
			payload,
			encode_multipart = False)

		if not response.status in [200, 201]:

			raise Exception (
				"Error %s: %s" % (
					response.status,
					response.reason))

	def create_raw (self, key, value):

		self.make_request (
			method = "PUT",
			url = self.key_url (key),
			payload_data = {
				"value": value,
				"prevExist": False,
			},
			accept_response = [ 201 ])

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

	def rm (self, key):

		self.make_request (
			method = "DELETE",
			url = self.key_url (key),
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

		result = self.etcd_client.write (
			key = self.prefix + key,
			value = None,
			append = True,
			dir = True)

		return (
			str (result.key [len (self.prefix):]),
			str (result.createdIndex),
		)

	def get_yaml (self, key):

		value_yaml = self.get_raw (key)
		value = yamlx.parse (value_yaml)

		return value

	def set_yaml (self, key, value, schema = None):

		value_yaml = yamlx.encode (schema, value)

		self.set_raw (key, value_yaml)

def args (sub_parsers):

	pass

# ex: noet ts=4 filetype=yaml

