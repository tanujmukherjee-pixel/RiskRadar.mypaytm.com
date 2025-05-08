from typing import List, Optional, AsyncGenerator
from ..domains.chat import ChatMessage, ChatResponse, Choice, Message
import uuid
import time
import logging
from ..services.react import react_query_engine
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from ..utils.file import read_file
from ..constants.path import SYSTEM_PROMPT_FILE, APPROACH_PROMPT_FILE, OUTPUT_PROMPT_FILE, PROMPTS_PATH, DOCS_PATH
import os
import shutil
import asyncio
from ..services.tools import tools_service
from ..rags.base import BaseRAG

logger = logging.getLogger(__name__)

class BaseAgent:

    agent_name = "default"
    agent = None
    tools = []

    def __init__(self,agent_name: str, tools: List[str]):
        self.agent_name = agent_name
        self.system_prompt = read_file(f"{PROMPTS_PATH}{SYSTEM_PROMPT_FILE}".format(agent_name=agent_name))
        self.approach_prompt = read_file(f"{PROMPTS_PATH}{APPROACH_PROMPT_FILE}".format(agent_name=agent_name))
        self.output_prompt = read_file(f"{PROMPTS_PATH}{OUTPUT_PROMPT_FILE}".format(agent_name=agent_name))
        self.tools = []
        for tool_name in tools:
            try:
                self.tools.append(tools_service.get_tool(tool_name))
            except Exception as e:
                logger.error(f"Error loading tool {tool_name} for agent {agent_name}: {e}")
        
        # Check if docs path exists
        docs_path = DOCS_PATH.format(agent_name=agent_name)
        if os.path.exists(docs_path):
            try:
                rag = BaseRAG(agent_name)
                query_engine_tool = QueryEngineTool(
                    query_engine=rag.get_query_engine(), 
                    metadata=ToolMetadata(
                        name=agent_name, 
                        description=f"Contains docs related to {agent_name}"
                    )
                )
                self.tools.append(query_engine_tool)
            except Exception as e:
                logger.error(f"Error setting up RAG for agent {agent_name}: {e}")

        self.agent = self.get_agent()

    def get_agent(self):
        return react_query_engine(self.system_prompt, self.approach_prompt, self.output_prompt, self.tools)

    def _get_reasoning_content(self, reasoning_step) -> str:
        """
        Safely extract reasoning content from different types of reasoning steps.
        
        This handles different step types that might have different attribute structures:
        - ThoughtReasoningStep has a 'thought' attribute
        - ObservationReasoningStep has a 'observation' attribute
        - Other step types might have different structures
        """
        try:
            # Check what attributes this step has
            if hasattr(reasoning_step, 'thought'):
                return reasoning_step.thought.replace("```", "")
            elif hasattr(reasoning_step, 'observation'):
                return f"Observation: {reasoning_step.observation}".replace("```", "")
            elif hasattr(reasoning_step, 'action'):
                action_input = getattr(reasoning_step, 'action_input', '')
                return f"Action: {reasoning_step.action} {action_input}".replace("```", "")
            else:
                # Fallback for unknown step types - try to extract something useful
                return str(reasoning_step).replace("```", "")
        except Exception as e:
            logger.warning(f"Error extracting reasoning content: {e}")
            return "Thinking..."

    async def chat_completion(self, messages: List[ChatMessage], max_tokens: Optional[int] = 50, temperature: Optional[float] = 0.7) -> AsyncGenerator[ChatResponse, None]:
        agent = self.get_agent()
        run_id = str(uuid.uuid4())
        temp_path = f"data/agents/{self.agent_name}/temp/{run_id}"

        try:
            message = ""
            for msg in messages:
                message += f"{msg.role}: {msg.content}\n"
            
            task = agent.create_task(message)

            # Handle first reasoning step
            step_output = await agent.arun_step(task.task_id)
            
            # Get first reasoning step content safely
            try:
                if task.extra_state and 'current_reasoning' in task.extra_state and len(task.extra_state['current_reasoning']) > 0:
                    reasoning_content = self._get_reasoning_content(task.extra_state['current_reasoning'][0])
                    
                    yield ChatResponse(
                        id=run_id,
                        object="chat.completion", 
                        created=int(time.time()),
                        model=self.agent_name,
                        choices=[
                            Choice(
                                index=0,
                                message=Message(role="assistant", reasoning_content=reasoning_content)
                            )
                        ]
                    )
            except Exception as e:
                logger.error(f"Error processing first reasoning step for agent {self.agent_name}: {e}")
                yield ChatResponse(
                    id=run_id,
                    object="chat.completion", 
                    created=int(time.time()),
                    model=self.agent_name,
                    choices=[
                        Choice(
                            index=0,
                            message=Message(role="assistant", reasoning_content="I'm thinking about your request...")
                        )
                    ]
                )

            # Continue with additional reasoning steps
            while not step_output.is_last:
                step_output = await agent.arun_step(task.task_id)
                
                try:
                    if task.extra_state and 'current_reasoning' in task.extra_state and len(task.extra_state['current_reasoning']) >= 1:
                        # Get the most appropriate reasoning step
                        reasoning_idx = min(len(task.extra_state['current_reasoning']) - 1, 0)
                        if len(task.extra_state['current_reasoning']) >= 2:
                            reasoning_idx = -2  # Second last is often more informative than the last
                            
                        reasoning_step = task.extra_state['current_reasoning'][reasoning_idx]
                        reasoning_content = self._get_reasoning_content(reasoning_step)
                        
                        yield ChatResponse(
                            id=run_id,
                            object="chat.completion", 
                            created=int(time.time()),
                            model=self.agent_name,
                            choices=[
                                Choice(
                                    index=0,
                                    message=Message(role="assistant", reasoning_content=reasoning_content)
                                )
                            ]
                        )
                except Exception as e:
                    logger.error(f"Error processing reasoning step for agent {self.agent_name}: {e}")
            
            # Generate final response
            try:
                response = await agent.afinalize_response(task.task_id)
                yield ChatResponse(
                    id=run_id,
                    object="chat.completion", 
                    created=int(time.time()),
                    model=self.agent_name,
                    choices=[
                        Choice(
                            index=0,
                            message=Message(role="assistant", content=str(response)),
                            finish_reason="stop"
                        )
                    ]
                )
            except Exception as e:
                logger.error(f"Error finalizing response for agent {self.agent_name}: {e}")
                yield ChatResponse(
                    id=run_id,
                    object="chat.completion", 
                    created=int(time.time()),
                    model=self.agent_name,
                    choices=[
                        Choice(
                            index=0,
                            message=Message(role="assistant", content="I apologize, but I encountered an error processing your request."),
                            finish_reason="stop"
                        )
                    ]
                )
        except Exception as e:
            logger.error(f"Unexpected error in chat_completion for agent {self.agent_name}: {e}")
            yield ChatResponse(
                id=run_id,
                object="chat.completion", 
                created=int(time.time()),
                model=self.agent_name,
                choices=[
                    Choice(
                        index=0,
                        message=Message(role="assistant", content="I apologize, but I encountered an unexpected error."),
                        finish_reason="stop"
                    )
                ]
            )
        finally:
            # Clean up in a non-blocking way
            if os.path.exists(temp_path):
                asyncio.create_task(self._cleanup_temp_dir(temp_path))
            return
    
    async def _cleanup_temp_dir(self, temp_path: str):
        """Asynchronously clean up temporary directory."""
        try:
            if os.path.exists(temp_path):
                shutil.rmtree(temp_path)
                logger.debug(f"Cleaned up temp directory: {temp_path}")
        except Exception as e:
            logger.error(f"Error cleaning up temp directory {temp_path}: {e}")
