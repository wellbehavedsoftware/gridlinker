from __future__ import absolute_import

import json
import ssl
import urllib3

from wbs.devops import yamlx

class Client:

	def __init__ (
		self,
		servers = [ "localhost" ],
		port = 2379,
		secure = False,
		client_ca_cert = None,
		client_cert = None,
		client_key = None,
	):

		self.servers = servers
		self.port = port

		if secure:

			self.http = urllib3.PoolManager (
				num_pools = 10,
				ca_certs = client_ca_cert,
				cert_file = client_cert,
				key_file = client_key,
				cert_reqs = ssl.CERT_REQUIRED)

			self.server_url = 'https://%s:%s' % (servers [0], port)

		else:

			self.http = urllib3.PoolManager (
				num_pools = 10)

			self.server_url = 'http://%s:%s' % (servers [0], port)

	def exists (self, key):

		response = self.http.request_encode_body (
			"GET",
			"%s/v2/keys%s" % (self.server_url, key))

		if response.status == 200:
			return True

		if response.status == 404:
			return False

		raise Exception ()

	def get_raw (self, key):

		response = self.http.request_encode_body (
			"GET",
			"%s/v2/keys%s" % (self.server_url, key))

		if response.status != 200:
			raise Exception ()

		value_etcd = json.loads (response.data)

		return value_etcd ["node"] ["value"]

	def set_raw (self, key, value):

		payload = {
			"value": value,
		}

		response = self.http.request_encode_body (
			"PUT",
			"%s/v2/keys%s" % (self.server_url, key),
			payload,
			encode_multipart = False)

		if not response.status in [200, 201]:
			raise Exception ()

	def rm (self, key):

		self.etcd_client.delete (
			key = key)

	def rmdir (self, key):

		self.etcd_client.delete (
			key = key,
			dir = True)

	def mkdir_queue (self, key):

		result = self.etcd_client.write (
			key = key,
			value = None,
			append = True,
			dir = True)

		return (
			str (result.key),
			str (result.createdIndex),
		)

	def get_yaml (self, key):

		value_yaml = self.get_raw (key)
		value = yamlx.parse (value_yaml)

		return value

	def set_yaml (self, key, value, schema = None):

		value_yaml = yamlx.encode (schema, value)

		self.set_raw (key, value_yaml)
