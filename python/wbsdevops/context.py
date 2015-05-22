from __future__ import absolute_import

import yaml

import wbsdevops
import wbsmisc

from wbsmisc import env_combine
from wbsmisc import lazy_property

class GenericContext (object):

	def __init__ (self, home, args):

		self.home = home
		self.args = args

	@lazy_property
	def client_config (self):

		file_path = "%s/config/client.yml" % self.home

		with open (file_path) as file_handle:
			return yaml.load (file_handle)

	@lazy_property
	def client (self):

		if self.client_config ["etcd_secure"] == "yes":

			return wbsdevops.Client (
				servers = self.client_config ["etcd_servers"],
				secure = True,
				client_ca_cert = "config/client-ca.cert",
				client_cert = "config/client.cert",
				client_key = "config/client.key",
				prefix = self.client_config ["etcd_prefix"])

		elif self.client_config ["etcd_secure"] == "no":

			return wbsdevops.Client (
				servers = self.client_config ["etcd_servers"],
				prefix = self.client_config ["etcd_prefix"])

		else:

			raise Exception ()

	@lazy_property
	def env (self):

		return env_combine (
			self.etcdctl_env,
			self.ansible_env)

	@lazy_property
	def etcdctl_env (self):

		if self.client_config ["etcd_secure"] == "yes":

			return {

				"ETCDCTL_PEERS": ",".join ([
					"https://%s:2379" % server
					for server in self.client_config ["etcd_servers"]
				]),

				"ETCDCTL_CA_FILE": "%s/config/client-ca.cert" % self.home,
				"ETCDCTL_CERT_FILE": "%s/config/client.cert" % self.home,
				"ETCDCTL_KEY_FILE": "%s/config/client.key" % self.home,

			}

		else:

			return {

				"ETCDCTL_PEERS": ",".join ([
					"http://%s:2379" % server
					for server in self.client_config ["etcd_servers"]
				]),

			}

	@lazy_property
	def third_party_home (self):

		return "%s/third-party" % self.home

	@lazy_property
	def ansible_home (self):

		return "%s/ansible" % self.third_party_home

	@lazy_property
	def ansible_env (self):

		return {

			"ANSIBLE_CONFIG": "work/ansible.cfg",
			"ANSIBLE_HOME": self.ansible_home,

			"PATH": [ "%s/bin" % self.ansible_home ],
			"PYTHONPATH": [ "%s/lib" % self.ansible_home ],
			"PYTHONUNBUFFERED": "1",

		}

	@lazy_property
	def ansible_config (self):

		return {

			"defaults": {
				"force_color": "True",
				"gathering": "explicit",
				"library": ":".join ([
					"%s/ansible-modules-core" % self.third_party_home,
					"%s/ansible-modules-extras" % self.third_party_home,
				]),
				"roles_path": "%s/roles" % self.home,
			},

			"ssh_connection": {
				"control_path": "%s/work/control/%%%%h" % self.home,
				"pipelining": "True",
				"ssh_args": " ".join ([
					"-o ControlMaster=auto",
					"-o ControlPersist=60s",
					"-o ForwardAgent=yes",
				]),
			},

		}

	@lazy_property
	def ansible_args (self):

		return [
			"--inventory-file", "%s/misc/inventory-script" % self.home,
			"--extra-vars", "@%s/config/overrides.yml" % self.home,
		]

	def ansible_init (self):

		pass

	@lazy_property
	def authorities (self):

		return LazyDictionary (
			self.load_authority)

	def load_authority (self, name):

		authority = CertificateAuthority (
			self,
			"/authority/" + name,
			self.certificate_data)

		authority.load ()

		return authority
