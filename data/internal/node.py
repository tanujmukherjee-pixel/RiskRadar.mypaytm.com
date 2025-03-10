from kubernetes import client, config

class Tools:
    def __init__(self):
        pass

    def get_node(node_name: str):
        try:
            config.load_incluster_config()
        except config.ConfigException:
            config.load_kube_config()
    
        v1 = client.CoreV1Api()
    
        try:
            node = v1.read_node(name=node_name)
        except client.exceptions.ApiException as e:
            error_message = f"Failed to read node {node_name}: {e}"
            print(error_message)
    
        return node