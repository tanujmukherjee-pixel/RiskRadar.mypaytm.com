from llama_index.llms.openai import OpenAI


def trim_context(context, max_tokens=1000):
    llm = OpenAI(
        model="gpt-4o",
        api_key="REDACTED_OPENAI_KEY",
    )

    response = llm.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are a data expert. You are given a context and you need to trim it to the most relevant information.",
            },
            {"role": "user", "content": context},
        ],
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content
