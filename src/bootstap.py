from .services.tools import tools_service
from .services.agent import agent_service
def bootstrap():
    tools_service.bootstrap()
    agent_service.bootstrap()