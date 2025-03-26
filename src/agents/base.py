from typing import List, Optional, AsyncGenerator
from ..domains.chat import ChatMessage, ChatResponse, Choice, Message
import uuid
import time
from ..services.react import react_query_engine
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from ..utils.file import read_file
from ..constants.path import SYSTEM_PROMPT_FILE, APPROACH_PROMPT_FILE, OUTPUT_PROMPT_FILE, PROMPTS_PATH, DOCS_PATH
import os
import shutil
from ..services.tools import tools_service
from ..rags.base import BaseRAG

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
            self.tools.append(tools_service.get_tool(tool_name))
        
        # Check if docs path exists
        docs_path = DOCS_PATH.format(agent_name=agent_name)
        if os.path.exists(docs_path):
            rag = BaseRAG(agent_name)
            query_engine_tool = QueryEngineTool(query_engine=rag.get_query_engine(), metadata=ToolMetadata(name=agent_name, description=f"Contains docs related to {agent_name}"))
            self.tools.append(query_engine_tool)

        self.agent = self.get_agent()

    def get_agent(self):
        return react_query_engine(self.system_prompt, self.approach_prompt, self.output_prompt, self.tools)

    async def chat_completion(self, messages: List[ChatMessage], max_tokens: Optional[int] = 50, temperature: Optional[float] = 0.7) -> AsyncGenerator[ChatResponse, None]:
        agent = self.get_agent()
        run_id = str(uuid.uuid4())

        message = ""
        for msg in messages:
            message += f"{msg.role}: {msg.content}\n"
        
        task = agent.create_task(message)

        # Handle first reasoning step
        try:
            step_output = agent.run_step(task.task_id)
            try:
                yield ChatResponse(
                    id=run_id,
                    object="chat.completion", 
                    created=int(time.time()),
                    model=self.agent_name,
                    choices=[
                        Choice(
                            index=0,
                            message=Message(role="assistant", reasoning_content=task.extra_state['current_reasoning'][0].thought.replace("```", ""))
                        )
                        ]
                    )
            except (IndexError, KeyError) as e:
                print(f"Error accessing reasoning content: {e}")
        except Exception as e:
            print(f"Error running first step: {e}")
            # Generate a generic response if the agent step fails
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
            try:
                step_output = agent.run_step(task.task_id)
                try:
                    # Access the second-to-last reasoning to avoid potential empty deque issues
                    reasoning_idx = -2 if len(task.extra_state['current_reasoning']) >= 2 else 0
                    reasoning_content = task.extra_state['current_reasoning'][reasoning_idx].thought.replace("```", "")
                    
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
                except (IndexError, KeyError) as e:
                    print(f"Error accessing reasoning content in step: {e}")
            except Exception as e:
                print(f"Error running step: {e}")
                break
        
        # Generate final response
        try:
            response = agent.finalize_response(task.task_id)
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
            print(f"Error finalizing response: {e}")
            # Provide a fallback response
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

        temp_path = f"data/agents/{self.agent_name}/temp/{run_id}"

        try:
            if os.path.exists(temp_path):
                shutil.rmtree(temp_path)
        except Exception as e:
            print(f"Error cleaning up temporary path: {e}")
