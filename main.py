from fastapi import FastAPI, HTTPException
from typing import Dict, Any, Optional
from agent.agent_loop import react_loop
from pydantic import BaseModel

from observability.langfuse_client import langfuse

app = FastAPI()


class ModelResponse(BaseModel):
    session_id: str
    message: str
    system: Optional[str] = None
    model: str = "qwen2.5:7b"
    params: Optional[Dict[str, Any]] = None


@app.get("/")
def home():
    return {"message": "Api active.."}


@app.post("/chat")
async def chat(config: ModelResponse):
    with langfuse.start_as_current_observation(
        name='chat_request',
        input={"message": config.message},
        metadata={"session_id": config.session_id}
    ) as trace:
        try:
            result = await react_loop(config.session_id, config.model, config.message, config.system, config.params)
            trace.update(output={"response": result})

            return {
                "status": "Success",
                "response": result
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Model failed to respond: {str(e)}"
            )
        finally:
            langfuse.flush()

