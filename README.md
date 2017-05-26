# vlcp-openstack-bridge

OpenStack Neutron ML2 plugin for VLCP SDN Controller

# INSTALL plugin

python setup.py install


# Prepare physicalnetwork
Neutron provider network and tenant network map to physicalnetwork with physicalport in vlcp, 
so first we should create physicalnetwork and physicalport . do it follow http://vlcp.readthedocs.io/

provider_physicalnetwork_id = `create physicalnetwork in vlcp`
physicalnetwork_port = `create physicalnetwork "physicalnetwork_id" physicalnetworkport 'eth0'`

tenant_physicalnetwork_id = `create physicalnetwork in vlcp`
physicalnetwork_port = `create physicalnetwork "physicalnetwork_id" physicalnetworkport 'eth1'


# config Neutron ml2 plugin

type_drivers = flat,vxlan,vlan
tenant_network_types=vxlan
vni_ranges=999:1009

mechanism_drivers=viperflow

# about viperflow controller
[viperflow]
# used to connect to vlcp controller
controller = http://xxxx:xx

provider_physicalnet_map = provider_name:provider_physicalnetwork_id   (provider_network_name : physicalnetworkid created in vlcp)

tenant_physicalnet_map = vxlan:tenant_physicalnetwork_id    (tenant_network_type: physicalnetworkid created in vlcp)


# restart Neutron 

# create network in provider network or tenant network.

# enjoy it !
