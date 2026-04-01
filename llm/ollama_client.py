from ollama import AsyncClient

url = "http://localhost:11434"
headers = {
    "Content-Type": "application/json"
}
client = AsyncClient(host=url, headers=headers)

from ollama import AsyncClient

url = "http://localhost:11434"

client = AsyncClient(host=url)


async def call_llm(messages, model, params=None):
    response = await client.chat(
        model=model,
        messages=messages,
        options=params,
        stream=False
    )

    return response.message.content


