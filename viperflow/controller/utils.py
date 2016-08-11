import json

def get_host_routes_from_subnets(subnets):
    
    host_routes = dict()

    jt = json.loads(subnets)

    for item in jt['result']:
        sid = item['id']
        routes = item['host_routes']
        
        host_routes[sid] = routes

    return host_routes
    
