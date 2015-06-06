from __future__ import absolute_import
from __future__ import unicode_literals

import os
import threading
import yaml

import gridlinker
import wbs

from wbs import env_combine
from wbs import lazy_property
from wbs import yamlx

from wbs import LazyDictionary
from wbs import SchemaDatabase

from gridlinker.certificate import CertificateAuthority

from gridlinker.generic.collection import GenericCollection

class GenericContext (object):

	def __init__ (self, home, connection_name, project_metadata):

		self.home = home
		self.connection_name = connection_name
		self.project_metadata = project_metadata

	@lazy_property
	def support_package (self):

		return "gridlinker.generic"

	@lazy_property
	def devops_script (self):

		return os.environ [
			self.project_metadata ["environment"] ["devops_script"]]

	@lazy_property
	def ansible_inventory_file (self):
	
		return "%s/misc/inventory-script" % self.wbs_devops_tools_home

	@lazy_property
	def certificate_data (self):

		return self.project_metadata ["certificate_data"]

	@lazy_property
	def connections_config (self):

		file_path = "%s/config/connections.yml" % self.home

		with open (file_path) as file_handle:
			return yaml.load (file_handle)

	@lazy_property
	def connection_config (self):

		if not self.connection_name in self.connections_config:

			raise Exception (
				"Connection is not configured: %s" % (
					self.connection_name))

		return self.connections_config [self.connection_name]

	@lazy_property
	def client (self):

		if self.connection_config ["etcd_secure"] == "yes":

			return gridlinker.Client (
				servers = self.connection_config ["etcd_servers"],
				secure = True,
				client_ca_cert = "config/%s-ca.cert" % self.connection_name,
				client_cert = "config/%s.cert" % self.connection_name,
				client_key = "config/%s.key" % self.connection_name,
				prefix = self.connection_config ["etcd_prefix"])

		elif self.connection_config ["etcd_secure"] == "no":

			return gridlinker.Client (
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

		return "%s/gridlinker" % self.third_party_home

	@lazy_property
	def ansible_env (self):

		return {

			"WBS_DEVOPS_PARENT_HOME": self.home,
			"WBS_DEVOPS_PARENT_WORK": "%s/work" % self.home,
			"WBS_DEVOPS_TOOLS_SUPPORT": self.support_package,
			"WBS_DEVOPS_KNOWN_HOSTS": "%s/work/known-hosts" % self.home,
			"WBS_DEVOPS_CONNECTION": self.connection_name,

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
			"%s/gridlinker/action-plugins" % self.third_party_home,
		]

	@lazy_property
	def ansible_lookup_plugins (self):

		return [
			"%s/gridlinker/lookup-plugins" % self.third_party_home,
		]

	@lazy_property
	def ansible_callback_plugins (self):

		return [
			"%s/gridlinker/callback-plugins" % self.third_party_home,
		]

	@lazy_property
	def ansible_filter_plugins (self):

		return [
			"%s/gridlinker/filter-plugins" % self.third_party_home,
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
			"--inventory-file", self.ansible_inventory_file,
			"--extra-vars", "@%s/config/overrides.yml" % self.home,
		]

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
			self.resources,
		]

	@lazy_property
	def admins (self):

		return GenericCollection (
			context = self,
			path = "/admin",
			type = "admin",
			schema = self.schemas ["admin"])

	@lazy_property
	def groups (self):

		return GenericCollection (
			context = self,
			path = "/group",
			type = "group",
			schema = self.schemas ["group"])

	@lazy_property
	def resources (self):

		return GenericCollection (
			context = self,
			path = "/resource",
			type = "resource",
			schema = self.schemas ["resource"])

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

			for resource_name, resource_data in self.resources.get_all_list ():

				if "class" in resource_data ["identity"]:

					class_name = resource_data ["identity"] ["class"]

				else:

					raise Exception ("TODO")

				class_data = self.local_data ["classes"] [class_name]

				if "ssh" in class_data \
				and "hostnames" in class_data ["ssh"]:

					addresses = map (
						lambda value: value.replace (
							"{{ inventory_hostname }}",
							resource_name),
						class_data ["ssh"] ["hostnames"])

				else:

					addresses = [ resource_name ] + sorted (set (filter (None, [
						resource_data.get ("private", {}).get ("address", None),
						resource_data.get ("public", {}).get ("address", None),
						resource_data.get ("amazon", {}).get ("public_ip", None),
						resource_data.get ("amazon", {}).get ("public_dns_name", None),
						resource_data.get ("amazon", {}).get ("private_ip", None),
						resource_data.get ("amazon", {}).get ("private_dns_name", None),
						resource_data.get ("ansible", {}).get ("ssh_host", None),
					])))

				if not addresses:
					continue

				for key_type in [ "rsa", "ecdsa" ]:

					if self.resources.exists_file (
						resource_name,
						"ssh-host-key/%s/public" % key_type):

						resource_key = self.resources.get_file (
							resource_name,
							"ssh-host-key/%s/public" % key_type)

						file_handle.write ("%s %s\n" % (
							",".join (addresses),
							resource_key,
						))

					elif "ssh" in resource_data \
					and "host_key_%s" % key_type in resource_data ["ssh"]:

						file_handle.write ("%s %s\n" % (
							",".join (addresses),
							resource_data ["ssh"] ["host_key_%s" % key_type],
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

	@lazy_property
	def classes (self):

		return self.local_data ["classes"]

# ex: noet ts=4 filetype=yaml
