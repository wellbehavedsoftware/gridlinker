from __future__ import absolute_import
from __future__ import unicode_literals

import os
import threading
import yaml

import wbsdevops
import wbsmisc

from wbsmisc import env_combine
from wbsmisc import lazy_property
from wbsmisc import yamlx

from wbsmisc import LazyDictionary
from wbsmisc import SchemaDatabase

from wbsdevops.certificate import CertificateAuthority

from wbsdevops.generic import GenericCollection

class GenericContext (object):

	def __init__ (self, home, connection_name, args):

		self.home = home
		self.connection_name = connection_name
		self.args = args

	@lazy_property
	def connections_config (self):

		file_path = "%s/config/connections.yml" % self.home

		with open (file_path) as file_handle:
			return yaml.load (file_handle)

	@lazy_property
	def connection_config (self):

		return self.connections_config [self.connection_name]

	@lazy_property
	def client (self):

		if self.connection_config ["etcd_secure"] == "yes":

			return wbsdevops.Client (
				servers = self.connection_config ["etcd_servers"],
				secure = True,
				client_ca_cert = "config/%s-ca.cert" % self.connection_name,
				client_cert = "config/%s.cert" % self.connection_name,
				client_key = "config/%s.key" % self.connection_name,
				prefix = self.connection_config ["etcd_prefix"])

		elif self.connection_config ["etcd_secure"] == "no":

			return wbsdevops.Client (
				servers = self.connection_config ["etcd_servers"],
				prefix = self.connection_config ["etcd_prefix"])

		else:

			raise Exception ()

	@lazy_property
	def env (self):

		return env_combine (
			self.etcdctl_env,
			self.ansible_env)

	@lazy_property
	def etcdctl_env (self):

		if self.connection_config ["etcd_secure"] == "yes":

			return {

				"ETCDCTL_PEERS": ",".join ([
					"https://%s:2379" % server
					for server in self.connection_config ["etcd_servers"]
				]),

				"ETCDCTL_CA_FILE": "%s/config/%s-ca.cert" % (
					self.home,
					self.connection_name,
				),

				"ETCDCTL_CERT_FILE": "%s/config/%s.cert" % (
					self.home,
					self.connection_name,
				),

				"ETCDCTL_KEY_FILE": "%s/config/%s.key" % (
					self.home,
					self.connection_name,
				),

			}

		else:

			return {

				"ETCDCTL_PEERS": ",".join ([
					"http://%s:2379" % server
					for server in self.connection_config ["etcd_servers"]
				]),

			}

	@lazy_property
	def third_party_home (self):

		return "%s/third-party" % self.home

	@lazy_property
	def ansible_home (self):

		return "%s/ansible" % self.third_party_home

	@lazy_property
	def wbs_devops_tools_home (self):

		return "%s/wbs-devops-tools" % self.third_party_home

	@lazy_property
	def ansible_env (self):

		return {

			"WBS_DEVOPS_PARENT_HOME": self.home,
			"WBS_DEVOPS_PARENT_WORK": "%s/work" % self.home,
			"WBS_DEVOPS_TOOLS_SUPPORT": self.support_package,
			"WBS_DEVOPS_KNOWN_HOSTS": "%s/work/known-hosts" % self.home,

			"ANSIBLE_CONFIG": "work/ansible.cfg",
			"ANSIBLE_HOME": self.ansible_home,

			"PATH": [ "%s/bin" % self.ansible_home ],
			"PYTHONPATH": [
				"%s/python" % self.home,
				"%s/python" % self.wbs_devops_tools_home,
				"%s/lib" % self.ansible_home,
			],
			"PYTHONUNBUFFERED": "1",

		}

	@lazy_property
	def ansible_action_plugins (self):

		return [
			"%s/wbs-devops-tools/action-plugins" % self.third_party_home,
		]

	@lazy_property
	def ansible_lookup_plugins (self):

		return [
			"%s/wbs-devops-tools/lookup-plugins" % self.third_party_home,
		]

	@lazy_property
	def ansible_callback_plugins (self):

		return [
			"%s/wbs-devops-tools/callback-plugins" % self.third_party_home,
		]

	@lazy_property
	def ansible_filter_plugins (self):

		return [
			"%s/wbs-devops-tools/filter-plugins" % self.third_party_home,
		]

	@lazy_property
	def ansible_library (self):

		return [
			"%s/ansible-modules-core" % self.third_party_home,
			"%s/ansible-modules-extras" % self.third_party_home,
			"%s/modules" % self.wbs_devops_tools_home,
		]

	@lazy_property
	def ansible_roles_path (self):

		roles_parent_dirs = [
			"%s/playbooks" % self.home,
			"%s/roles" % self.wbs_devops_tools_home,
		]

		return [
			"%s/%s" % (roles_parent_dir, roles_dir)
			for roles_parent_dir in roles_parent_dirs
			for roles_dir in os.listdir (roles_parent_dir)
			if os.path.isdir ("%s/%s" % (roles_parent_dir, roles_dir))
		]

	@lazy_property
	def ansible_ssh_args (self):

		return [
			"-o ControlMaster=auto",
			"-o ControlPersist=60s",
			"-o ForwardAgent=yes",
		]

	@lazy_property
	def ansible_config (self):

		return {

			"defaults": {
				"force_color": "True",
				"gathering": "explicit",
				"library": ":".join (self.ansible_library),
				"action_plugins": ":".join (self.ansible_action_plugins),
				"filter_plugins": ":".join (self.ansible_filter_plugins),
				"lookup_plugins": ":".join (self.ansible_lookup_plugins),
				"callback_plugins": ":".join (self.ansible_callback_plugins),
				"roles_path": ":".join (self.ansible_roles_path),
			},

			"ssh_connection": {
				"control_path": "%s/work/control/%%%%h" % self.home,
				"pipelining": "True",
				"ssh_args": " ".join (self.ansible_ssh_args),
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

	@lazy_property
	def collections (self):

		return [
			self.admins,
			self.groups,
			self.hosts,
			self.amazon_accounts,
			self.amazon_balancers,
			self.amazon_vpcs,
		]

	@lazy_property
	def admins (self):

		return GenericCollection (self, "/admin", self.schemas ["admin"])

	@lazy_property
	def groups (self):

		return GenericCollection (self, "/group", self.schemas ["group"])

	@lazy_property
	def hosts (self):

		return GenericCollection (self, "/host", self.schemas ["host"])

	@lazy_property
	def amazon_accounts (self):

		return GenericCollection (self, "/amazon/account", self.schemas ["amazon-account"])

	@lazy_property
	def amazon_balancers (self):

		return GenericCollection (self, "/amazon/balancer", self.schemas ["amazon-balancer"])

	@lazy_property
	def amazon_vpcs (self):

		return GenericCollection (self, "/amazon/vpc", self.schemas ["amazon-vpc"])

	@lazy_property
	def local_data (self):

		return yamlx.load_data ("%s/data" % self.home)

	@lazy_property
	def overrides_data (self):

		return yamlx.load_data ("config/overrides.yml")

	@lazy_property
	def wbs_devops_tools_data (self):

		return yamlx.load_data ("%s/data" % self.wbs_devops_tools_home)

	@lazy_property
	def schemas (self):

		schemas = SchemaDatabase ()
		
		schemas.read_all (self.wbs_devops_tools_data ["schemas"])
		schemas.read_all (self.local_data ["schemas"])

		return schemas

	@lazy_property
	def ansible_ssh_args (self):

		return [
			"-o ControlMaster=auto",
			"-o ControlPersist=60s",
			"-o ForwardAgent=yes",
			"-o StrictHostKeyChecking=yes",
			"-o UserKnownHostsFile=%s/work/known-hosts" % self.home,
		]

	def ansible_init (self):

		with open ("%s/work/known-hosts" % self.home, "w") as file_handle:

			for host_name, host_data in self.hosts.get_all_list ():

				addresses = [ host_name ] + sorted (set (filter (None, [
					host_data.get ("private_address", None),
					host_data.get ("public_address", None),
					host_data.get ("amazon_public_ip", None),
					host_data.get ("amazon_public_dns_name", None),
					host_data.get ("amazon_private_ip", None),
					host_data.get ("amazon_private_dns_name", None),
				])))

				for key_type in [ "rsa", "ecdsa" ]:

					if self.hosts.exists_file (
						host_name,
						"ssh-host-key/%s/public" % key_type):

						host_key = self.hosts.get_file (
							host_name,
							"ssh-host-key/%s/public" % key_type)

						file_handle.write ("%s %s\n" % (
							",".join (addresses),
							host_key,
						))

					elif "ssh_host_key_%s" % key_type in host_data:

						file_handle.write ("%s %s\n" % (
							",".join (addresses),
							host_data ["ssh_host_key_%s" % key_type],
						))

		for key_path, key_data in self.client.get_tree ("/ssh-key"):

			if not key_path.endswith ("/private"):
				continue

			key_name = key_path [ 1 : - len ("/private") ]

			if not os.path.isdir ("%s/work/ssh-keys" % self.home):
				os.mkdir ("%s/work/ssh-keys" % self.home)

			file_path = "%s/work/ssh-keys/%s" % (self.home, key_name)

			with open (file_path, "w") as file_handle:
				os.fchmod (file_handle.fileno (), 0o600)
				file_handle.write (key_data)

# ex: noet ts=4 filetype=yaml
