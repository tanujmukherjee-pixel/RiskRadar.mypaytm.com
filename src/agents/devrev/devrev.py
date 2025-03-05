from ..base import BaseAgent
from typing import List, Optional, AsyncGenerator
from ...domains.chat import ChatMessage, ChatResponse, Choice, Message, Usage
from .llm.react import react_query_engine
import uuid
import os
import shutil

class DevRevAgent(BaseAgent):
    def __init__(self):
        super().__init__()

    async def chat_completion(self, messages: List[ChatMessage], max_tokens: Optional[int] = 50, temperature: Optional[float] = 0.7) -> AsyncGenerator[ChatResponse, None]:
        agent = self.get_agent()
        run_id = str(uuid.uuid4())

        message = f"Session ID: {run_id}\n"
        for msg in messages:
            message += f"{msg.role}: {msg.content}\n"
        
        task = agent.create_task(message)

        step_output = agent.run_step(task.task_id)

        try :
            yield ChatResponse(
                id=run_id,
                object="chat.completion", 
                created=1234567890,
                model="dev-rev",
                choices=[
                    Choice(
                        index=0,
                        message=Message(role="assistant", content="Thinking:\n``` " + task.extra_state['current_reasoning'][0].thought + "```\n")
                    )
                    ]
                )
        except Exception as e:
            print(e)

        while not step_output.is_last:
            try :
                step_output = agent.run_step(task.task_id)
                yield ChatResponse(
                    id=run_id,
                    object="chat.completion", 
                    created=1234567890,
                    model="dev-rev",
                    choices=[
                            Choice(
                                index=0,
                                message=Message(role="assistant", content="``` " + task.extra_state['current_reasoning'][-2].thought + "```\n")
                            )
                        ]
                    )
            except Exception as e:
                print(e)
        
        response = agent.finalize_response(task.task_id)
        yield ChatResponse(
            id=run_id,
            object="chat.completion", 
            created=1234567890,
            model="dev-rev",
            choices=[
                Choice(
                    index=0,
                    message=Message(role="assistant", content=str(response)),
                    finish_reason="stop"
                )
            ]
        )

    def get_agent(self):
        return react_query_engine()
