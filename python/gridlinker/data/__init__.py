from __future__ import absolute_import
from __future__ import unicode_literals

from wbs import register_error

from gridlinker.data import resource

def args (parser):
	resource.args (parser)

register_error (
	name = "resource_name_mismatch",
	short = """
		Resource name '{resource_name}' does not match expected name
		'{expected_resource_name}'
	""",
	long = """
		The resource name does not match the expected value. The name consists
		of the namespace defined by the class (class_namespace) and the
		resource's short name (identity_name), separated by a forwardslash. A
		mismatch can be caused by changing the namespace without updated the
		resource data correctly, or by modifying the resource data directly.
	""")

register_error (
	name = "resource_parent_not_set",
	short = """
		Resource '{resource_name}' of class '{class_name}' should have a parent
	""",
	long = """
		The specified resource should have a parent, according to the specified
		class, but none is specified. Ensure you specify --parent when creating
		a new resource on the command line. This can also happen if the class is
		modified without updating the existing resource data.
	""")

register_error (
	name = "resource_parent_does_not_exist",
	short = """
		Parent '{parent_name}' of resource '{resource_name}' does not exist
	""",
	long = """
		The parent of the specified resource does not exist. The parent name is
		determined as the parent namespace specified in the resource's class
		(class_parent_namespace) and the parent name specified in the resource
		(identity_parent), separated by a slash. If you are creating a new
		resource, ensure that the specified parent name exists.
	""")

register_error (
	name = "resource_parent_set",
	short = """
		Resource '{resource_name}' of class '{class_name}' should not have a
		parent
	""",
	long = """
		The specified resource should not have a parent, according to the
		specified class, but a parent is specified. Ensure you do not pass
		--parent when creating a new resource of this type on the command line.
		This can also happen if the class is modified without updating the
		existing resource data.
	""")

# ex: noet ts=4 filetype=yaml
