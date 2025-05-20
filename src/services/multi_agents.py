import logging
from .model import model_service
import asyncio
from ..repositories.multi_agent import get_repository
from concurrent.futures import ThreadPoolExecutor
from ..multi_agents.base import BaseMultiAgent

logger = logging.getLogger(__name__)

class MultiAgentsService:
    def __init__(self):
        self.model_service = model_service
        self.multi_agent_repository = get_repository()
        # Thread pool for CPU-bound operations
        self._executor = ThreadPoolExecutor(max_workers=10)
        pass

    async def bootstrap(self):
        logger.info("Bootstrapping multi agents")

        # Run database query in thread pool
        loop = asyncio.get_event_loop()
        multi_agents = await loop.run_in_executor(
            self._executor,
            self.multi_agent_repository.list_multi_agents
        )

        for multi_agent in multi_agents:
            logger.info(f"Bootstrapping multi agent: {multi_agent['name']}")
            await self.bootstrap_multi_agent(multi_agent)

    async def bootstrap_multi_agent(self, multi_agent):
        logger.info(f"Bootstrapping multi agent: {multi_agent['name']}")
        all_agents_loaded = False
        while not all_agents_loaded:
            all_agents_loaded = True
            for agent in multi_agent['agents']:
                try:
                    model = await self.model_service._get_model(agent['name'])
                    if not model:
                        logger.error(f"Agent {agent['name']} not found")
                        all_agents_loaded = False
                        break
                    logger.info(f"Agent {agent['name']} found")
                except ValueError:
                    logger.error(f"Agent {agent['name']} not found")
                    all_agents_loaded = False
                    break
            
            if not all_agents_loaded:
                # Wait a bit before checking again
                await asyncio.sleep(5)
        
        initial_agent = await self.model_service._get_model(multi_agent['initial_agent'])
        if not initial_agent:
            logger.error(f"Initial agent {multi_agent['initial_agent']} not found")
            return
        
        all_agents = []
        for agent in multi_agent['agents']:
            model = await self.model_service._get_model(agent['name'])
            if not model:
                logger.error(f"Agent {agent['name']} not found")
                continue
            all_agents.append(model)

        multi_agent_instance = BaseMultiAgent(initial_agent, all_agents)
        await model_service.add_model(multi_agent['name'], multi_agent_instance)

# Singleton instance
multi_agents_service = MultiAgentsService()