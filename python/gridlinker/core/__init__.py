from __future__ import absolute_import
from __future__ import unicode_literals

from gridlinker.core import context
from gridlinker.core.context import GenericContext

from gridlinker.core import metadata

from gridlinker.core import inventory
from gridlinker.core.inventory import Inventory

from wbs import register_error

register_error (
	name = "connection_config_missing",
	short = "No such file: config/connections.yml",
	long = """
		Your connections file is not missing. This is required to connect to the
		etcd database where all of the runtime data is stored. Please refer to
		the documentation for more information.
	""")

register_error (
	name = "connection_config_invalid",
	short = "File format invalid: config/connections.yml",
	long = """
		Your connections file is not valid YAML. Please check the syntax and
		try again.
	""")

register_error (
	name = "connection_config_not_dict",
	short = "Data structure invalid: config/connections.yml",
	long = """
		Your connections file should be a YAML 'dict' at the top level. Please
		check the contents and try again, or refer to the documentation.
	""")

register_error (
	name = "connection_not_configured",
	short = "Connection is not configured: {connection_name}",
	long = """
		Please ensure that you are using the correct connection name, and that
		this is configured correctly in config/connections.yml.
	""")

register_error (
	name = "connection_ca_cert_missing",
	short = "CA certificate missing: config/{connection_name}-ca.cert",
	long = """
		The CA certificate for the etcd database connection is not present.
		Please obtain this file and ensure it is placed in the correct location.
	""")

register_error (
	name = "connection_cert_missing",
	short = "Certificate missing: config/{connection_name}.cert",
	long = """
		The certificate for the etcd database connection is not present. Please
		obtain this file and ensure it is placed in the correct location.
	""")

register_error (
	name = "connection_key_missing",
	short = "Private key missing: config/{connection_name}.key",
	long = """
		The private key for the etcd database connection is not present. Please
		obtain this file and ensure it is placed in the correct location.
	""")

register_error (
	name = "inventory_referenced_resource_does_not_exist",
	short = """
		Resource '{referenced_resource_name}', referenced by '{resource_name}'
		as '{reference_name}', does not exist
	""",
	long = """
		The referenced resource, as defined in the referencing resources class,
		does not exist.
	""")

# ex: noet ts=4 filetype=yaml
