import urllib
import urllib2

from oslo_log import log
from viperflow.common import config
from viperflow.controller import utils
from neutron.extensions import providernet

LOG = log.getLogger(__name__)

class Controller(object):
    def __init__(self):
        self.conn = config.getconnection()
        self.timeout = config.getconntimeout()

        self._check_physicalnetwork_config()
        
    def _check_physicalnetwork_config(self):
        providermap = config.getprovidermap()
        tenantmap = config.gettenantmap()
        
        # this used to record providernetwork:physicalnetworkid
        self.providermap = {}
        # this used to record tenant network type:physicalnetworkid
        self.tenantmap = {}

        for item in providermap.split(','):
            m = item.partition(':')
            if m[1] and m[2]:
                self.providermap[m[0]] = m[2]
        
        for item in tenantmap.split(','):
            m = item.partition(':')
            if m[0] and m[1]:
                self.tenantmap[m[0]] = m[2]

        # list all physicalnetwork , assert physicalnetwork id in controller

    def createlogicalnetwork(self,physicalnetwork,physicalnetworktype,segid,network):
        
        n = dict()
        if physicalnetwork:
            physicalnetworkid = self.providermap[physicalnetwork]
        else:
            if physicalnetworktype:
                physicalnetworkid = self.tenantmap[physicalnetworktype]

        n['physicalnetwork'] = physicalnetworkid
        n['name'] = network['name']
        n['admin_state_up'] = network['admin_state_up']
        n['mtu'] = network['mtu']
        n['id'] = network['id']
        
        if physicalnetworktype == 'vlan':
            n['vlanid'] = segid
        else:
            n['vni'] = segid


        # viperflow only support one subnet, so get first one
        if network['subnets']:
            n['subnet'] = network.get('subnets')[0]
        
        LOG.info(" --- createlogicalnetwork -- %r",n)
        param = urllib.urlencode(n)
        LOG.info(" -- param -- %r",param)
        url = self.conn + "/viperflow/createlogicalnetwork?%s" % param

        urllib2.urlopen(url,timeout=self.timeout).read()
        
    def deletelogicalnetwork(self,networkid):
        
        param = urllib.urlencode({"id":networkid})
        url = self.conn + "/viperflow/deletelogicalnetwork?%s" % param

        urllib2.urlopen(url,timeout=self.timeout).read()
        
    def updatelogicalnetwork(self,item):
        LOG.info("---- updatelogicalnetwork ---")
        param = urllib.urlencode(item)
        url = self.conn + "/viperflow/updatelogicalnetwork?%s" % param

        urllib2.urlopen(url,timeout=self.timeout).read()
    def createlogicalport(self,port):
        LOG.info("---- createlogicalport ----")
        p = dict()
        
        p['id'] = port['id']
        p['logicalnetwork'] = port['network_id']
        p['name'] = port['name']
        p['mac_address'] = port['mac_address']
        
		# create router with subnet , it will createlogicalport first ipaddress == gateway
		# viperflow will auto add this router port, so return here
		if port['device_owner'] == "network:router_interface":
			return
		
        if port['fixed_ips']:
            p['subnet'] = port['fixed_ips'][0]['subnet_id']
            p['ip_address'] = port['fixed_ips'][0]['ip_address']
            
            # when create dhcp port , we should add static route
            # to metadata server on dhcp server
            if port['device_owner'] == "network:dhcp":
                
                staticroute = [config.getmetadataaddress(),p['ip_address']]

                # first get subnet routes info, add all
                subnets = self.listsubnet(id = p['subnet'])
                
                # {subnetid: routes,subnetid2:routes}
                routes = utils.get_host_routes_from_subnets(subnets)[p['subnet']]
                
                if staticroute not in routes:
                    routes.append(staticroute)
                    
                    s = dict()
                    s['id'] = p['subnet']
                    s['host_routes'] = '`' + str(routes) + '`'
                    
                    self._updatesubnet(**s)


        param = urllib.urlencode(p)
        url = self.conn + "/viperflow/createlogicalport?%s" % param

        urllib2.urlopen(url,timeout=self.timeout).read()
    def updatelogicalport(self,port):
        LOG.info("---- updatelogicalport ---")
        
        p = dict()
        
        p['id'] = port['id']
        p['name'] = port['name']
        p['mac_address'] = port['mac_address']
		
		if port['device_owner'] == "network:router_interface":
			return
			
        param = urllib.urlencode(p)
        url = self.conn + "/viperflow/updatelogicalport?%s" % param

        urllib2.urlopen(url,timeout=self.timeout).read()
    def deletelogicalport(self,port):
        LOG.info("---- deletelogicalport ---")
        portid = port['id']
		
		if port['device_owner'] == "network:router_interface":
			return
		
        if port['fixed_ips']:
            #p['subnet'] = port['fixed_ips'][0]['subnet_id']
            subnetid = port['fixed_ips'][0]['subnet_id']
            #p['ip_address'] = port['fixed_ips'][0]['ip_address']
            ipaddress = port['fixed_ips'][0]['ip_address']
            
            # when delete dhcp port , we should remove static route
            # to metadata server on dhcp server
            if port['device_owner'] == "network:dhcp":
                
                staticroute = [config.getmetadataaddress(),ipaddress]

                # first get subnet routes info, add all
                subnets = self.listsubnet(id = subnetid)
                
                # {subnetid: routes,subnetid2:routes}
                routes = utils.get_host_routes_from_subnets(subnets)[subnetid]
                
                if staticroute in routes:
                    routes.remove(staticroute)
                    
                    s = dict()
                    s['id'] = subnetid
                    s['host_routes'] = '`' + str(routes) + '`'
                    
                    self._updatesubnet(**s)

        param = urllib.urlencode({"id":portid})
        url = self.conn + "/viperflow/deletelogicalport?%s" % param
        urllib2.urlopen(url,timeout=self.timeout).read()
    
    def createsubnet(self,subnet):

        s = dict()

        s['id'] = subnet['id']
        s['name'] = subnet['name']
        s['logicalnetwork'] = subnet['network_id']
        
        s['cidr'] = subnet['cidr']
        #openstack have multi allocated segment ip ,
        #now controller support only one segment,
        #so get first segment from openstack
        s['allocated_start'] = subnet['allocation_pools'][0]['start']
        s['allocated_end'] = subnet['allocation_pools'][0]['end']
        
        s['gateway'] = subnet['gateway_ip']
        s['enable_dhcp'] = subnet['enable_dhcp']
        
        s['dns_nameservers'] = subnet['dns_nameservers']

        routes = []
        for item in subnet['host_routes']:
            destination = item['destination']
            nexthop = item['nexthop']
            
            #
            # not allow add metadata address static route  
            #
            if destination == config.getmetadataaddress():
                continue
            
            routes.append([destination,nexthop])
        
        s['host_routes'] = '`' + str(routes) + '`'

        param = urllib.urlencode(s)
        url = self.conn + "/viperflow/createsubnet?%s" % param
        urllib2.urlopen(url,timeout=self.timeout).read()
    
    def updatesubnet(self,subnet,origin_subnet):

        s = dict()

        s['id'] = subnet['id']
        s['name'] = subnet['name']
        s['logicalnetwork'] = subnet['network_id']
        
        # subnet is not allowd update cidr
        #s['cidr'] = subnet['cidr']
        
        #openstack have multi allocated segment ip ,
        #now controller support only one segment,
        #so get first segment from openstack
        s['allocated_start'] = subnet['allocation_pools'][0]['start']
        s['allocated_end'] = subnet['allocation_pools'][0]['end']
        
        s['gateway'] = subnet['gateway_ip']
        s['enable_dhcp'] = subnet['enable_dhcp']
        
        s['dns_nameservers'] = subnet['dns_nameservers']

        #
        #   here means update host_routes, first get routes 
        #   add dhcp metadata static routes
        #
        if origin_subnet['host_routes'] != subnet['host_routes']:
            
            newroutes = []
            for item in subnet['host_routes']:
                destination = item["destination"]
                nexthop = item['nexthop']

                if destination == config.getmetadataaddress():
                    continue
                
                newroutes.append([destination,nexthop])
            
            
            # find metadata static route , append to newroute
            subnets = self.listsubnet(id = s['id']) 
            routes = utils.get_host_routes_from_subnets(subnets)[s['id']]
            
            for des,nh in routes:
                if des == config.getmetadataaddress():
                    newroutes.append([des,nh])
            
            s['host_routes'] = '`' + str(newroutes) + '`'
             
        self._updatesubnet(**s)
    
    def _updatesubnet(self,**kwargs):
        
        param = urllib.urlencode(kwargs)
        url = self.conn + "/viperflow/updatesubnet?%s" % param
        urllib2.urlopen(url,timeout=self.timeout).read()

    def deletesubnet(self,subnetid):
        
        param = urllib.urlencode({"id":subnetid})
        url = self.conn + "/viperflow/deletesubnet?%s" % param
        urllib2.urlopen(url,timeout=self.timeout).read()
    
    def listsubnet(self,**kwargs):
        
        s = dict()
        s.update(kwargs)

        param = urllib.urlencode(s)

        url = self.conn + "/viperflow/listsubnets?%s" % param

        f = urllib2.urlopen(url,timeout=self.timeout)
        
        subnets = f.read()

        f.close()
        
        return subnets
	
	def createvirtualrouter(self,router):
		
		r = dict()
		
		r['id'] = router['id']
		r['name'] = router['name']
		r['routes'] = '`' + str(router['routes']) + '`'
		
		param = urllib.urlencode(r)
		
		url = self.conn + "/vrouterapi/createvirtualrouter?%s" % param
		
		urllib2.urlopen(url,timeout=self.timeout).read()
	
	def deletevirtualrouter(self,routerid):
		
		r = dict()
		
		r['id'] = router['id']
		
		param = urllib.urlencode(r)
		
		url = self.conn + "/vrouterapi/deletevirtualrouter?%s" % param
		
		urllib2.urlopen(url,timeout=self.timeout).read()
		
	def updatevirtualrouter(self,id,router):
		
		r = dict()
		
		r['id'] = router['id']
		
		param = urllib.urlencode(r)
		
		url = self.conn + "/vrouterapi/updatevirtualrouter?%s" % param
		
		#urllib2.urlopen(url,timeout = self.timeout).read()
	
	def addrouterinterface(self,id,subnet,**kwargs):
		
		r = dict()
		
		r["router"] = id
		r["subnet"] = subnet
		
		param = urllib.urlencode(r)
		
		url = self.conn + "/vrouterapi/addrouterinterface?%s" % param
		
		urllib2.urlopen(url,timeout = self.timeout).read()
	
	def removerouterinterface(self,id):
		
		r = dict()
		
		r["id"] = id
		
		param = urllib.urlencode(r)
		
		url = self.conn + "/vrouterapi/removerouterinterface?%s" % param
		
		urllib2.urlopen(url,timeout = self.timeout).read()