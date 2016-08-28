from __future__ import absolute_import
from __future__ import unicode_literals

from netaddr import IPNetwork

def ip_network (value):

	return IPNetwork (value).network

def ip_netmask (value):

	return IPNetwork (value).netmask

def ip_reverse_zones (value):

	network = IPNetwork (value)

	if network.prefixlen > 24:

		return [
			"%s.%s.%s.%s.in-addr.arpa." % (
				octet,
				network.network.words [2],
				network.network.words [1],
				network.network.words [0])
			for octet
			in xrange (
				network.network.words [3],
				network.broadcast.words [3] + 1)
		]

	elif network.prefixlen > 16:

		return [
			"%s.%s.%s.in-addr.arpa." % (
				octet,
				network.network.words [1],
				network.network.words [0])
			for octet
			in xrange (
				network.network.words [2],
				network.broadcast.words [2] + 1)
		]

	elif network.prefixlen > 8:

		return [
			"%s.%s.in-addr.arpa." % (
				octet,
				network.network.words [0])
			for octet
			in xrange (
				network.network.words [1],
				network.broadcast.words [1] + 1)
		]

	else:

		raise Exception ()

class FilterModule (object):

    def filters (self):

        return {

			"ip_network": ip_network,
			"ip_netmask": ip_netmask,

			"ip_reverse_zones": ip_reverse_zones,

		}

# ex: noet ts=4 filetype=python
