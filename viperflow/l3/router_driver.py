from oslo_log import log

from neutron.db import common_db_mixin
from neutron.db import extraroute_db
from neutron.services import service_base
from neutron.plugins.common import constants
from viperflow.controller import controller

Log = log.getLogger(__name__)

class ViperflowL3RouterPlugin(service_base.ServicePluginBase,
								common_db_mixin.CommonDBMixin,
								extraroute_db.ExtraRoute_dbonly_mixin):
	
	supported_extension_aliases = ["router","extrarouter"]
	
	def __init__(self):
		Log.info(" ----- start viperflow l3 plugin -----")
		super(ViperflowL3RouterPlugin,self).__init__()
		self.controller = controller.Controller()
		
	def get_plugin_type(self):
		return constants.L3_ROUTER_NAT
		
	def get_plugin_description(self):
		return "L3 Router Service Plugin for basic L3 forwarding using viperflow"
		
	def create_router(self,context,router):
		Log.info(" ---- create_router -- %r",router)
		router = super(ViperflowL3RouterPlugin,self).
					create_router(context,router)
		
		self.controller.createvirtualrouter(router)
		
		return router
	
	def delete_router(self,context,id):
		
		Log.info("--- delete_router -- %r",id)
		router = super(ViperflowL3RouterPlugin,self).delete_router(context,id)
		
		self.controller.deletevirtualrouter(id)
		
		return router
	
	def update_router(self,context,id,router):
		
		original_router = self.get_router(context,id)
		new_router = super(ViperflowL3RouterPlugin,self).update_router(
						context,id,router)
		Log.info("----- update_router ---- original_router %r",original_router)
		Log.info("----- update_router ---- new_router %r",new_router)
		
		self.controller.updatevirtualrouter(id,router)
		
		return new_router
		
	def add_router_interface(self,context,router_id,interface_info):
		Log.info("---- add router id %r---- ",router_id)
		Log.info("---- add router interface_info %r",interface_info)
		
		rif = super(ViperflowL3RouterPlugin,self).add_router_interface(
					context,router_id,interface_info)
		
		info = dict()
		
		# special one port as router port, in viperflow delete this port, 
		# special this port ipaddress as router port ipaddress
		# when remove this router port , we create this port in viperflow
		if "port_id" in interface_info:
			pass
		
		if "subnet_id" in interface_info:
			info['subnet'] = interface_info["subnet_id"]
		
		self.controller.addrouterinterface(router_id,**info)
		return rif
	
	def remove_router_interface(self,context,router_id,interface_info):
		Log.info("---- remove router id %r---- ",router_id)
		Log.info("---- remove router interface_info %r",interface_info)
		
		rif = super(ViperflowL3RouterPlugin,self).remove_router_interface(
					context,router_id,interface_info)
		
		info = dict()
		
		if "port_id" in interface_info:
			pass
		
		if "subnet_id" in interface_info:
			info["subnet"] = interface_info["subnet_id"]
		
		self.controller.removerouterinterface(router_id,**info)
		return rif