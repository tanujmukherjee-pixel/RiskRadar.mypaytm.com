from typing import List, AsyncGenerator
from ..agents.base import BaseAgent
from ..domains.chat import ChatMessage, ChatResponse
from typing import Optional
from ..domains.state import State, StateAgent

class BaseMultiAgent:
    def __init__(self, initial_agent: BaseAgent, all_agents: List[StateAgent]):
        self.state = State()
        self.state.current_agent = initial_agent
        self.state.all_agents = all_agents

    async def _get_available_agents(self):
        available_agents = []
        # Append all agents except the current one
        for state_agent in self.state.all_agents:
            if state_agent.agent != self.state.current_agent and state_agent not in available_agents:
                available_agents.append(state_agent)
        return available_agents

    async def _next_step(self):
        self.state.is_done = True

    async def _handle_transition(self):
        if self.state.is_interrupted or self.state.is_done:
            return             

    async def _execute_current_agent(self, max_tokens: Optional[int] = 50, temperature: Optional[float] = 0.7) -> AsyncGenerator[ChatResponse, None]:
        while not self.state.is_interrupted and not self.state.is_done:
            agent = self.state.current_agent
            async for response in agent.chat_completion(self.state.messages, max_tokens, temperature):
                message = response.choices[0].message
                message.role = agent.agent_name
                self.state.messages.append(message)
                yield response
            await self._next_step()
            await self._handle_transition()

    async def chat_completion(self, messages: List[ChatMessage], max_tokens: Optional[int] = 50, temperature: Optional[float] = 0.7) -> AsyncGenerator[ChatResponse, None]:
        self.state.messages.extend(messages)
        async for response in self._execute_current_agent(max_tokens, temperature):
            yield response
