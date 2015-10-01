from __future__ import absolute_import
from __future__ import unicode_literals

from gridlinker.tools import arguments
from gridlinker.tools.arguments import ArgumentGroup
from gridlinker.tools.arguments import ClassArgument
from gridlinker.tools.arguments import GeneratePasswordArgument
from gridlinker.tools.arguments import IndexArgument
from gridlinker.tools.arguments import MiscAddArgument
from gridlinker.tools.arguments import MiscRemoveArgument
from gridlinker.tools.arguments import MiscSetArgument
from gridlinker.tools.arguments import MiscSetDictArgument
from gridlinker.tools.arguments import MiscSetFileArgument
from gridlinker.tools.arguments import MiscUnsetArgument
from gridlinker.tools.arguments import MiscUnsetDictArgument
from gridlinker.tools.arguments import NameArgument
from gridlinker.tools.arguments import NamespaceArgument
from gridlinker.tools.arguments import ParentArgument

from gridlinker.tools import command
from gridlinker.tools.command import GenericCommand
from gridlinker.tools.command import CommandHelper

from gridlinker.tools import columns
from gridlinker.tools.columns import SimpleColumn
from gridlinker.tools.columns import UniqueNameColumn

from gridlinker.tools import env

from wbs import register_error

def args (parser):
	env.args (parser)

register_error (
	name = "editor_not_configured",
	short = "No text editor has been configured",
	long = """
		Please configure a text editor by setting either the VISUAL or EDITOR
		environment variable.
	""")

# ex: noet ts=4 filetype=yaml
