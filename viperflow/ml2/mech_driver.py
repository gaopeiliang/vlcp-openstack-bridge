from oslo_log import log
from oslo_config import cfg
from neutron.plugins.ml2 import driver_api
from neutron.extensions import providernet
from neutron.extensions import portbindings

from viperflow.common import config
from viperflow.controller import controller
LOG = log.getLogger(__name__)

class ViperflowMechanismDriver(driver_api.MechanismDriver):

    def initialize(self):
        LOG.info("starting ViperflowMechanismDriver")
        
        LOG.info(" ml2 tenant_network_types = %r",cfg.CONF.ml2.tenant_network_types)
        LOG.info(" ml2 viperflow = %r",cfg.CONF.viperflow.controller)
        LOG.info(" ml2 viperflow = %r",cfg.CONF.viperflow.connection_timeout)
        LOG.info(" ml2 viperflow = %r",cfg.CONF.viperflow.provider_physicalnet_map)
        LOG.info(" ml2 viperflow = %r",cfg.CONF.viperflow.tenant_physicalnet_map)

        self.controller = controller.Controller()
        
        self.vif_type = portbindings.VIF_TYPE_OVS
        self.vif_details = {}
    def create_network_postcommit(self,context):
        LOG.info("-- create_network_postcommit --")
        
        network = context.current

        LOG.info("-- network = %r --",network)

        physnet = network.get(providernet.PHYSICAL_NETWORK)
        segid = network.get(providernet.SEGMENTATION_ID)
        networktype = network.get(providernet.NETWORK_TYPE)

        self.controller.createlogicalnetwork(physnet,networktype,segid,network)
    def delete_network_postcommit(self,context):
        LOG.info("-- delete_network_postcommit --")
        network = context.current
        LOG.info("-- delete network = %r--",network)

        self.controller.deletelogicalnetwork(network['id'])

    def update_network_postcommit(self,context):
        LOG.info(" -- update_network_postcommit --")
        network = context.current
        original_network = context.original
        
        #
        # update network only (admin_state_up,
        # name,shared,router:external,port_security_enabled)
        # only "name" is controller care , 
        # so only update name when name is different 
        #

        if network['name'] != original_network['name']:
            updateitems = {'id':network['id'],"name":network['name']}
            self.controller.updatelogicalnetwork(updateitems)
        
        LOG.info(" -- network = %r",network)
        LOG.info(" -- original network = %r",original_network)
    def create_port_postcommit(self,context):
        LOG.info(" -- create_port_postcommit --")
        port = context.current
        
        LOG.info(" --- create port = %r",port)
        self.controller.createlogicalport(port)
    def delete_port_postcommit(self,context):
        LOG.info(" -- delete_port_postcommit --")
        
        port = context.current

        LOG.info(" -- delete port = %r",port)
        self.controller.deletelogicalport(port['id'])
    def update_port_postcommit(self,context):
        LOG.info(" -- update_port_postcommit --")
        port = context.current
        original_port = context.original
        LOG.info(" --- update port = %r",port)
        LOG.info(" -- update original port = %r",original_port)
        
        # now controller only care such attr change ,,
        # will add after ...
        if port['name'] != original_port['name']\
            or port['mac_address'] != original_port['mac_address']:
            self.controller.updatelogicalport(port)
    def bind_port(self,context):
        port = context.current
         
        LOG.info(" --- bind port = %r",port)

        for segment_to_bind in context.segments_to_bind:
            LOG.info(" --- segments_to_bind -- %r",segment_to_bind)
            context.set_binding(segment_to_bind[driver_api.ID],
                        self.vif_type,
                        self.vif_details)
