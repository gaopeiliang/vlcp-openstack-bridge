import urllib
import urllib2

from oslo_log import log
from viperflow.common import config
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
        n['id'] = netwoork['id']
        
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
        
        # now we do not support security group , and l3
        # so we ignore ip , subnet , security group info

        param = urllib.urlencode(p)
        url = self.conn + "/viperflow/createlogicalport?%s" % param

        urllib2.urlopen(url,timeout=self.timeout).read()
    def updatelogicalport(self,port):
        LOG.info("---- updatelogicalport ---")
        
        p = dict()
        
        p['id'] = port['id']
        p['name'] = port['name']
        p['mac_address'] = port['mac_address']

        param = urllib.urlencode(p)
        url = self.conn + "/viperflow/updatelogicalport?%s" % param

        urllib2.urlopen(url,timeout=self.timeout).read()
    def deletelogicalport(self,portid):
        LOG.info("---- deletelogicalport ---")

        param = urllib.urlencode({"id":portid})
        url = self.conn + "/viperflow/deletelogicalport?%s" % param
        urllib2.urlopen(url,timeout=self.timeout).read()

