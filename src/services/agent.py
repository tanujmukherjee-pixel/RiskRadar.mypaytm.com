from ..agents.base import BaseAgent
from ..domain.agent_request import AgentRequest
from ..services.model import model_service
from ..constants.path import PROMPTS_PATH, SYSTEM_PROMPT_FILE, APPROACH_PROMPT_FILE, OUTPUT_PROMPT_FILE, DOCS_PATH
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging
from ..repositories.agent import get_repository as get_agent_repository
from ..repositories.noop_agent import get_repository as get_noop_agent_repository
from ..utils.s3 import fetch_docs_from_s3

logger = logging.getLogger(__name__)

class AgentService:
    def __init__(self):
        self.model_service = model_service
        
        # Thread safety locking
        self._agents_lock = asyncio.Lock()
        
        # Thread pool for CPU-bound operations
        self._executor = ThreadPoolExecutor(max_workers=10)
        
        if os.getenv("DISABLE_DATABASE"):
            self.agent_repository = get_noop_agent_repository()
        else:
            self.agent_repository = get_agent_repository()

    async def create_agent(self, agent_request: AgentRequest, prompts: dict):
        """Create a new agent with thread safety and concurrency."""
        agent_data = {
            "name": agent_request.name,
            "description": agent_request.description,
            "tools": ",".join(agent_request.list_of_tools),
            "system_prompt": prompts[SYSTEM_PROMPT_FILE],
            "approach_prompt": prompts[APPROACH_PROMPT_FILE],
            "output_prompt": prompts[OUTPUT_PROMPT_FILE]
        }
        
        # Run database operations in thread pool
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            self._executor,
            lambda: self.agent_repository.create_agent(agent_data)
        )
        
        # Save prompts to disk
        await self._save_prompts(agent_request.name, prompts)

        print(f"Saving prompts to disk: {agent_request.name}")

        # Fetch docs from s3
        await self.fetch_docs_from_s3(agent_request.name)
        
        # Create and register the agent
        agent = BaseAgent(agent_request.name, agent_request.list_of_tools)
        await self.model_service.add_model(agent_request.name, agent)
        
        logger.info(f"Agent '{agent_request.name}' created")
        return agent
    
    async def fetch_docs_from_s3(self, agent_name: str):
        """Fetch docs from s3 and save to disk."""
        try:
            print(f"Fetching docs from s3: {agent_name}")
            await fetch_docs_from_s3(agent_name, f"{DOCS_PATH.format(agent_name=agent_name)}/")
        except Exception as e:
            logger.error(f"Error fetching docs from s3: {e}")
            raise e

    async def delete_agent(self, agent_name: str):
        """Delete an agent with thread safety and concurrency."""
        try:
            # Run database operations in thread pool
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                self._executor,
                lambda: self.agent_repository.delete_agent(agent_name)
            )
            
            # Remove from model service
            await self.model_service.delete_model(agent_name)
            
            # Delete prompts
            prompts_path = PROMPTS_PATH.format(agent_name=agent_name)
            if os.path.exists(prompts_path):
                # Delete prompt files
                for file_name in [SYSTEM_PROMPT_FILE, APPROACH_PROMPT_FILE, OUTPUT_PROMPT_FILE]:
                    file_path = f"{prompts_path}{file_name}"
                    if os.path.exists(file_path):
                        await loop.run_in_executor(
                            self._executor,
                            lambda: os.remove(file_path)
                        )
                
                # Try to remove the directory
                try:
                    await loop.run_in_executor(
                        self._executor,
                        lambda: os.rmdir(prompts_path)
                    )
                except OSError:
                    # Directory might not be empty, which is fine
                    pass
                    
            logger.info(f"Agent '{agent_name}' deleted")
        except Exception as e:
            logger.error(f"Error deleting agent {agent_name}: {str(e)}")
            raise

    async def bootstrap(self):
        """Bootstrap agents with concurrency."""
        logger.info("Bootstrapping agents")
        
        # Run database query in thread pool
        loop = asyncio.get_event_loop()
        agents = await loop.run_in_executor(
            self._executor,
            self.agent_repository.list_agents
        )
        
        # Process agents concurrently
        tasks = []
        for agent in agents:
            task = asyncio.create_task(self._bootstrap_agent(agent))
            tasks.append(task)
            
        # Wait for all agents to be bootstrapped
        await asyncio.gather(*tasks)
        
        logger.info(f"Agents bootstrapped - {len(agents)} agents loaded")

    async def _bootstrap_agent(self, agent):
        """Bootstrap a single agent concurrently."""
        try:
            prompts = {
                SYSTEM_PROMPT_FILE: agent['system_prompt'],
                APPROACH_PROMPT_FILE: agent['approach_prompt'],
                OUTPUT_PROMPT_FILE: agent['output_prompt']
            }
            
            # Save prompts to disk
            await self._save_prompts(agent['name'], prompts)
            
            await self.fetch_docs_from_s3(agent['name'])

            # Create base agent - this could be CPU intensive
            loop = asyncio.get_event_loop()
            base_agent = await loop.run_in_executor(
                self._executor,
                lambda: BaseAgent(agent['name'], agent['tools'].split(","))
            )
            
            # Add to model service
            await self.model_service.add_model(agent['name'], base_agent)
            
            logger.info(f"Agent '{agent['name']}' bootstrapped")
        except Exception as e:
            logger.error(f"Error bootstrapping agent {agent['name']}: {str(e)}")

    async def _save_prompts(self, agent_name: str, prompts: dict):
        """Save prompts to disk with concurrency."""
        folder_path = PROMPTS_PATH.format(agent_name=agent_name)
        
        # Create directory if needed
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        
        # Save prompt files concurrently
        tasks = []
        for prompt_file, content in prompts.items():
            file_path = f"{folder_path}{prompt_file}"
            task = self._save_prompt_file(file_path, content)
            tasks.append(task)
            
        # Wait for all files to be written
        await asyncio.gather(*tasks)
        
    async def _save_prompt_file(self, file_path: str, content: str):
        """Save a single prompt file with thread pool for I/O operations."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            self._executor,
            lambda: self._write_file(file_path, content)
        )
        
    def _write_file(self, file_path: str, content: str):
        """Write a file synchronously."""
        with open(file_path, "w") as f:
            f.write(content)

# Singleton instance
agent_service = AgentService()