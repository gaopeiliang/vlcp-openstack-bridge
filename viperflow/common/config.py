from oslo_config import cfg

viperflow_opts = [
        cfg.StrOpt('controller',
                    default='http://127.0.0.1:8181',
                    help='The URL string connect to controller'
                    ),
        cfg.IntOpt('connection_timeout',
                    default=10,
                    help='call controller API timeout'
                    ),
        cfg.StrOpt('provider_physicalnet_map',
                    help='openstack provider network map to physicalnetwork id'        
                    ),
        cfg.StrOpt('tenant_physicalnet_map',
                    help='openstack tenant network map to physicalnetwork id'
                    )
    ]

cfg.CONF.register_opts(viperflow_opts,group='viperflow')


def getconnection():
    return cfg.CONF.viperflow.controller

def getconntimeout():
    return cfg.CONF.viperflow.connection_timeout 

def getprovidermap():
    return cfg.CONF.viperflow.provider_physicalnet_map

def gettenantmap():
    return cfg.CONF.viperflow.tenant_physicalnet_map
