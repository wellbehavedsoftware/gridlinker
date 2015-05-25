from __future__ import absolute_import

import json
import ssl
import urllib3

from wbsmisc import yamlx

class Client:

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
		self.prefix = prefix

		if secure:

			self.http = urllib3.PoolManager (
				num_pools = 10,
				ca_certs = client_ca_cert,
				cert_file = client_cert,
				key_file = client_key,
				cert_reqs = ssl.CERT_REQUIRED)

			self.server_url = "https://%s:%s" % (servers [0], port)

		else:

			self.http = urllib3.PoolManager (
				num_pools = 10)

			self.server_url = "http://%s:%s" % (servers [0], port)

	def key_url (self, key):

		url_string = "%s/v2/keys%s%s" % (
			self.server_url,
			self.prefix,
			key)

		return url_string.encode ("utf-8")

	def exists (self, key):

		response = self.http.request (
			"GET",
			self.key_url (key))

		if response.status == 200:
			return True

		if response.status == 404:
			return False

		raise Exception ()

	def get_raw (self, key):

		response = self.http.request (
			"GET",
			self.key_url (key))

		if response.status == 404:

			raise LookupError (
				"No such key: %s" % key)

		if response.status != 200:

			raise Exception (
				"Error %s: %s" % (
					response.status,
					response.reason))

		value_etcd = json.loads (response.data)

		return value_etcd ["node"] ["value"]

	def set_raw (self, key, value):

		payload = {
			"value": value,
		}

		response = self.http.request_encode_body (
			"PUT",
			self.key_url (key),
			payload,
			encode_multipart = False)

		if not response.status in [200, 201]:

			raise Exception (
				"Error %s: %s" % (
					response.status,
					response.reason))

	def update_raw (self, key, old_value, new_value):

		payload = {
			"prevValue": old_value,
			"value": new_value,
		}

		response = self.http.request_encode_body (
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

		payload = {
			"value": value,
			"prevExist": False,
		}

		response = self.http.request_encode_body (
			"PUT",
			self.key_url (key),
			payload,
			encode_multipart = False)

		if not response.status in [200, 201]:

			raise Exception (
				"Error %s: %s" % (
					response.status,
					response.reason))

	def get_tree (self, key):

		payload = {
			"recursive": "true",
		}

		response = self.http.request (
			"GET",
			self.key_url (key),
			payload)

		if response.status == 404:

			raise LookupError (
				"No such key: %s" % key)

		if not response.status in [200, 201]:

			raise Exception (
				"Error %s: %s" % (
					response.status,
					response.reason))

		tree_etcd = json.loads (response.data)

		return self.walk_tree (key, tree_etcd ["node"])

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

		self.etcd_client.delete (
			key = self.prefix + key)

	def rmdir (self, key):

		self.etcd_client.delete (
			key = self.prefix + key,
			dir = True)

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

# ex: noet ts=4 filetype=yaml
