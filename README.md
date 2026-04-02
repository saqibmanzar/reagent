# LLM API — Agentic Runtime from Scratch

A lightweight, model-agnostic **ReAct agent runtime** built from first principles using FastAPI and Ollama. Designed to be a transparent, hackable alternative to LangChain-style abstractions — every layer of the agent loop is explicit and inspectable.

Full observability via **Langfuse** with nested span tracing across every agent step.

---

## Architecture

```
POST /chat
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│                    FastAPI (main.py)                     │
│         Langfuse trace: chat_request                     │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│               Memory Manager                            │
│   fetch_memory(session_id, message, system)             │
│   • Builds history_message  (LLM input)                 │
│   • Manages chat + session state (in-memory)            │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│            ReAct Loop  (agent_loop.py)                  │
│            MAX_STEPS = 6                                │
│                                                         │
│   ┌─────────────────────────────────────────────────┐  │
│   │  Langfuse span: agent_step                      │  │
│   │                                                 │  │
│   │  1. llm_call  (generation span)                 │  │
│   │       └─► Ollama async client                   │  │
│   │                                                 │  │
│   │  2. parser  (span)                              │  │
│   │       └─► JSON output → ToolCall | FinalAnswer  │  │
│   │                                                 │  │
│   │  3a. tool_execution  (tool span)  ──────────┐   │  │
│   │       └─► Tool Router → Tool Function       │   │  │
│   │       └─► Result appended to history        │   │  │
│   │       └─► Loop continues ◄──────────────────┘   │  │
│   │                                                 │  │
│   │  3b. final_answer  (span)                       │  │
│   │       └─► update_session → return answer        │  │
│   └─────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
              Response: { status, response }
```

### Key Design Decisions

- **Model-agnostic JSON output** — the LLM is prompted to respond in structured JSON (`tool_call` | `final_answer`), no native Ollama tool-calling used. Works with any model that can follow JSON instructions.
- **Explicit tool registry** — tools are registered as `ToolSchema` objects with name, description, input schema, and a direct function reference. No magic decorators.
- **In-memory session management** — conversation history is keyed by `session_id`, making multi-turn interactions stateful without a database.
- **Nested Langfuse tracing** — every agent step, LLM call, parse, tool execution, and final answer is a separate span, giving full visibility into agent behavior.

---

## Project Structure

```
reagent/
├── main.py                   # FastAPI app, /chat endpoint
├── agent/
│   ├── agent_loop.py         # ReAct loop with Langfuse instrumentation
│   ├── response_parser.py    # Parses raw LLM JSON → ToolCall | FinalAnswer
│   └── models.py             # Pydantic models (ToolCall, FinalAnswer, ResponseError)
├── llm/
│   └── ollama_client.py      # Async Ollama client
├── memory_manager/
│   └── memory.py             # In-memory session + history manager
├── tools/
│   ├── calculator.py         # Calculator tool (sympy-based)
│   ├── tool_router.py        # Routes tool_call → function
│   ├── tools_registry.py     # Registers available tools
│   └── tools_schema.py       # ToolSchema Pydantic model
├── observability/
│   └── langfuse_client.py    # Langfuse client init
└── prompts/
    └── system_prompt.py      # System prompt builder (tool injection)
```

---

## Setup & Installation

### Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip
- [Ollama](https://ollama.com) running locally
- A [Langfuse](https://langfuse.com) account (cloud or self-hosted)

### 1. Clone & install dependencies

```bash
git clone https://github.com/saqibmanzar/reagent.git
cd llm-api
uv sync          # or: pip install -r requirements.txt
```

### 2. Configure environment variables

Create a `.env` file in the project root:

```env
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_HOST=https://cloud.langfuse.com   # or your self-hosted URL
```

### 3. Pull the model via Ollama

```bash
ollama pull qwen2.5:7b
```

### 4. Run the server

```bash
uv run fastapi dev ./main.py
```

Server starts at `http://localhost:8000`.

---

## API Usage

### `POST /chat`

Send a message to the agent. Supports multi-turn conversations via `session_id`.

**Request body:**

```json
{
  "session_id": "user-123",
  "message": "What is (2^100 + 3^50) mod 7?",
  "model": "qwen2.5:7b",
  "system": null,
  "params": null
}
```

| Field        | Type   | Required | Description                                      |
|--------------|--------|----------|--------------------------------------------------|
| `session_id` | string | ✅       | Identifies the conversation session              |
| `message`    | string | ✅       | User message                                     |
| `model`      | string | ✅       | Ollama model name (default: `qwen2.5:7b`)        |
| `system`     | string | ❌       | Optional system prompt override                  |
| `params`     | object | ❌       | Optional model params (temperature, etc.)        |

**Response:**

```json
{
  "status": "Success",
  "response": "Answer: 4. Explanation: The expression (2^100 + 3^50) mod 7 evaluates to 4."
}
```

### Example — cURL

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "demo-session",
    "message": "What is (2^100 + 3^50) mod 7?",
    "model": "qwen2.5:7b"
  }'
```

### Example — Python

```python
import httpx

response = httpx.post("http://localhost:8000/chat", json={
    "session_id": "demo-session",
    "message": "What is (2^100 + 3^50) mod 7?",
    "model": "qwen2.5:7b"
})
print(response.json())
```

---

## Available Tools

| Tool         | Description                              | Input                        |
|--------------|------------------------------------------|------------------------------|
| `calculator` | Arithmetic expression evaluator (sympy)  | `{ "expression": "string" }` |

### Adding a new tool

1. Create your tool function in `tools/`:

```python
# tools/my_tool.py
def my_tool(param: str) -> str:
    return f"result for {param}"
```

2. Register it in `tools/tools_registry.py`:

```python
from tools.my_tool import my_tool

available_tools = {
    "my_tool": ToolSchema(
        name="my_tool",
        description="Description the LLM will see",
        input_schema={
            "type": "object",
            "properties": {"param": {"type": "string"}},
            "required": ["param"]
        },
        function_reference=my_tool
    )
}
```

That's it — the tool is automatically injected into the system prompt and routed by the agent.

---

## Observability

Every request is traced end-to-end in Langfuse with the following span hierarchy:

```
trace: chat_request
  └── span: agent_step  (repeated per ReAct step)
        ├── generation: llm_call
        ├── span: parser
        ├── tool: tool_execution   (if tool called)
        └── span: final_answer     (on completion)
```

Open your Langfuse dashboard to inspect token usage, latency per step, tool inputs/outputs, and full conversation history.

---

## Roadmap

- [ ] Python sandbox code execution tool
- [ ] File editor tool (read / write / patch)
- [ ] LangGraph integration
- [ ] RAGAS evaluation pipeline
- [ ] Self-healing: agent fixes its own bugs via file tools

---

## Tech Stack

| Layer          | Technology                  |
|----------------|-----------------------------|
| Runtime        | Python 3.11, FastAPI, uv    |
| LLM inference  | Ollama (`qwen2.5:7b`)       |
| Agent pattern  | ReAct (from scratch)        |
| Observability  | Langfuse                    |
| Validation     | Pydantic v2                 |
| Math tools     | sympy                       |
