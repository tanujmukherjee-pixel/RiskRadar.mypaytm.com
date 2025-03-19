from ..base import BaseAgent

class SelfHealAgent(BaseAgent):
    def __init__(self):
        super().__init__("self-heal",["drain_node", "cordon_node", "uncordon_node", "get_dns_hostname", "clean_up_node", "get_node", "install_awscli", "get_node_instance_id"])