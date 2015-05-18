from __future__ import absolute_import

import etcd

from wbs.devops import yamlx

class Client:

	def __init__ (
		self,
		peers = None,
		ca_cert = None,
		client_cert = None,
		client_key = None,
		prefix = "",
	):

		self.prefix = prefix

		if peers:

			self.etcd_client = etcd.Client (
				protocol = "https",
				host = peers,
				cert = (client_cert, client_key),
				ca_cert = ca_cert)

		else:

			self.etcd_client = etcd.client.Client (
				host = "localhost",
				port = 2379)

	def exists (self, key):

		try:

			self.etcd_client.get (
				key = self.prefix + key)

			return True

		except etcd.EtcdKeyNotFound:

			return False

	def get_raw (self, key):

		value_etcd = self.etcd_client.get (
			key = self.prefix + key)

		return value_etcd.value

	def set_raw (self, key, value):

		self.etcd_client.write (
			key = self.prefix + key,
			value = value)

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
