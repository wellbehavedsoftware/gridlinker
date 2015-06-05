from __future__ import absolute_import
from __future__ import unicode_literals

from netaddr import IPNetwork

def ip_network (value):

	return IPNetwork (value).network

def ip_netmask (value):

	return IPNetwork (value).netmask

class FilterModule (object):

    def filters (self):

        return {

			"ip_network": ip_network,
			"ip_netmask": ip_netmask,

		}

# ex: noet ts=4 filetype=python
