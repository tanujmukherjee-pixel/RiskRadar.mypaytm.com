from ..agents.base import BaseAgent
from ..domain.agent_request import AgentRequest
from ..services.model import model_service
from ..constants.path import PROMPTS_PATH, SYSTEM_PROMPT_FILE, APPROACH_PROMPT_FILE, OUTPUT_PROMPT_FILE
import os
from ..repositories.agent import get_repository as get_agent_repository
from ..repositories.noop_agent import get_repository as get_noop_agent_repository

class AgentService:
    def __init__(self):
        self.model_service = model_service
        if os.getenv("DISABLE_DATABASE"):
            self.agent_repository = get_noop_agent_repository()
        else:
            self.agent_repository = get_agent_repository()

    def create_agent(self, agent_request: AgentRequest, prompts: dict):
        agent_data = {
            "name": agent_request.name,
            "description": agent_request.description,
            "tools": ",".join(agent_request.list_of_tools),
            "system_prompt": prompts[SYSTEM_PROMPT_FILE],
            "approach_prompt": prompts[APPROACH_PROMPT_FILE],
            "output_prompt": prompts[OUTPUT_PROMPT_FILE]
        }
        self.agent_repository.create_agent(agent_data)
        self._save_prompts(agent_request.name, prompts)
        agent = BaseAgent(agent_request.name, agent_request.list_of_tools)
        self.model_service.add_model(agent_request.name, agent)
        return agent
    
    def delete_agent(self, agent_name: str):
        self.agent_repository.delete_agent(agent_name)
        self.model_service.delete_model(agent_name)
        os.remove(PROMPTS_PATH.format(agent_name=agent_name))

    def bootstrap(self):
        print("Bootstrapping agents")
        agents = self.agent_repository.list_agents()
        for agent in agents:
            prompts = {
                SYSTEM_PROMPT_FILE: agent['system_prompt'],
                APPROACH_PROMPT_FILE: agent['approach_prompt'],
                OUTPUT_PROMPT_FILE: agent['output_prompt']
            }
            self._save_prompts(agent['name'], prompts)
            base_agent = BaseAgent(agent['name'], agent['tools'].split(","))
            self.model_service.add_model(agent['name'], base_agent)
        print("Agents bootstrapped")

    def _save_prompts(self, agent_name: str, prompts: dict):
        for prompt in prompts:
            folder_path = PROMPTS_PATH.format(agent_name=agent_name)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            with open(f"{folder_path}{prompt}", "w") as f:
                f.write(prompts[prompt])


agent_service = AgentService()