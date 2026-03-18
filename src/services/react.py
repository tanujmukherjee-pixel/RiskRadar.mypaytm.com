"""ReAct agent using Claude via Anthropic SDK."""

import os
from typing import Any, Sequence

import anthropic
from llama_index.core import PromptTemplate
from llama_index.core.agent import ReActAgent
from llama_index.core.base.llms.types import (
    ChatMessage,
    ChatResponse,
    ChatResponseGen,
    CompletionResponse,
    CompletionResponseGen,
    LLMMetadata,
)
from llama_index.core.llms import CustomLLM
from llama_index.core.llms.callbacks import llm_chat_callback, llm_completion_callback

react_system_header_str = """\
## Tools
You have access to a wide variety of tools. You are responsible for using
the tools in any sequence you deem appropriate to complete the task at hand.
This may require breaking the task into subtasks and using different tools
to complete each subtask.

You have access to the following tools:
{tool_desc}

## Output Format
To answer the question, please use the following format.

Thought: I need to use a tool to help me answer the question.
Action: tool name (one of {tool_names}) if using a tool.
Action Input: the input to the tool, in a JSON format representing the kwargs (e.g. {{"input": "hello world", "num_beams": 5}})


Please ALWAYS start with a Thought.

Please use a valid JSON format for the Action Input. Do NOT do this {{'input': 'hello world', 'num_beams': 5}}.

If this format is used, the user will respond in the following format:

Observation: response


You should keep repeating the above format until you have enough information
to answer the question without using any more tools. At that point, you MUST respond
in the one of the following two formats:

Thought: I can answer without using any more tools.
Answer: [your answer here]


Thought: I cannot answer the question with the provided tools.
Answer: Sorry, I cannot answer your query.

<IMPORTANT>Only respond with Answer if you have enough information to answer the question for rest of the conversation respond with Thought and Action. If you need to use a tool or fetch more information, respond with Thought and Action.</IMPORTANT>

## Additional Rules
- The answer MUST contain a sequence of bullet points that explain how you arrived at the answer. This can include aspects of the previous conversation history.
- You MUST obey the function signature of each tool. Do NOT pass in no arguments if the function expects arguments.

## Current Conversation
Below is the current conversation consisting of interleaving human and assistant messages.

"""


class ClaudeLLM(CustomLLM):
    """Custom LLM wrapper around Anthropic SDK."""

    model_name: str = "claude-sonnet-4-6"
    max_tokens: int = 4096
    context_window: int = 200000

    @property
    def metadata(self) -> LLMMetadata:
        """LLM metadata."""
        return LLMMetadata(
            context_window=self.context_window,
            num_output=self.max_tokens,
            model_name=self.model_name,
        )

    def _get_client(self) -> anthropic.Anthropic:
        kwargs: dict = {"api_key": os.environ.get("ANTHROPIC_API_KEY")}
        if base_url := os.environ.get("ANTHROPIC_BASE_URL"):
            kwargs["base_url"] = base_url
        return anthropic.Anthropic(**kwargs)

    @llm_completion_callback()
    def complete(self, prompt: str, **kwargs: Any) -> CompletionResponse:
        """Complete a prompt."""
        client = self._get_client()
        message = client.messages.create(
            model=self.model_name,
            max_tokens=self.max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        text = next(
            (
                b.text
                for b in message.content
                if isinstance(b, anthropic.types.TextBlock)
            ),
            "",
        )
        return CompletionResponse(text=text)

    @llm_completion_callback()
    def stream_complete(self, prompt: str, **kwargs: Any) -> CompletionResponseGen:
        """Stream complete a prompt."""
        client = self._get_client()
        with client.messages.stream(
            model=self.model_name,
            max_tokens=self.max_tokens,
            messages=[{"role": "user", "content": prompt}],
        ) as stream:
            full_text = ""
            for text_chunk in stream.text_stream:
                full_text += text_chunk
                yield CompletionResponse(text=full_text, delta=text_chunk)

    @llm_chat_callback()
    def chat(self, messages: Sequence[ChatMessage], **kwargs: Any) -> ChatResponse:
        """Chat with the LLM."""
        client = self._get_client()
        anthropic_messages = [
            {"role": m.role.value, "content": m.content}
            for m in messages
            if m.role.value in ("user", "assistant")
        ]
        system = next((m.content for m in messages if m.role.value == "system"), None)
        create_kwargs: dict[str, Any] = dict(
            model=self.model_name,
            max_tokens=self.max_tokens,
            messages=anthropic_messages,
        )
        if system:
            create_kwargs["system"] = system
        message = client.messages.create(**create_kwargs)
        text = next(
            (
                b.text
                for b in message.content
                if isinstance(b, anthropic.types.TextBlock)
            ),
            "",
        )
        return ChatResponse(message=ChatMessage(role="assistant", content=text))

    @llm_chat_callback()
    def stream_chat(
        self, messages: Sequence[ChatMessage], **kwargs: Any
    ) -> ChatResponseGen:
        """Stream chat with the LLM."""
        client = self._get_client()
        anthropic_messages = [
            {"role": m.role.value, "content": m.content}
            for m in messages
            if m.role.value in ("user", "assistant")
        ]
        system = next((m.content for m in messages if m.role.value == "system"), None)
        create_kwargs: dict[str, Any] = dict(
            model=self.model_name,
            max_tokens=self.max_tokens,
            messages=anthropic_messages,
        )
        if system:
            create_kwargs["system"] = system
        with client.messages.stream(**create_kwargs) as stream:
            full_text = ""
            for text_chunk in stream.text_stream:
                full_text += text_chunk
                yield ChatResponse(
                    message=ChatMessage(role="assistant", content=full_text),
                    delta=text_chunk,
                )


def react_query_engine(system_prompt, approach_prompt, output_prompt, tools):
    """
    Creates and returns a ReAct agent that utilizes both the query engine and Kibana logs fetcher.
    """
    llm = ClaudeLLM(
        model_name=os.environ.get("LLM_MODEL", "claude-sonnet-4-6"),
    )

    # Create the ReAct agent
    agent = ReActAgent.from_tools(tools, llm=llm, verbose=True, max_iterations=50)

    react_system_prompt = PromptTemplate(
        template=system_prompt
        + "\n\n## Approach\n\n"
        + approach_prompt
        + "\n\n## Final Answer\n\n"
        + output_prompt
        + "\n\n"
        + react_system_header_str
    )

    agent.update_prompts({"agent_worker:system_prompt": react_system_prompt})

    agent.reset()

    if os.environ.get("ENABLE_PROMPT"):
        prompt_dict = agent.get_prompts()
        for k, v in prompt_dict.items():
            print(f"Prompt: {k}\n\nValue: {v.template}")
    return agent
