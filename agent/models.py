from pydantic import BaseModel
from enum import Enum
from typing import Any, Literal

class ResponseType(str, Enum):
    TOOL_CALL = "tool_call"
    FINAL_ANSWER = "final_answer"


class ToolCall(BaseModel):
    type: ResponseType
    tool: str
    arguments: dict[str, Any]


class FinalAnswer(BaseModel):
    type: ResponseType
    final_answer: Any
    explanation: str | None = None
 

class ResponseError(BaseModel):
    type: Literal["error"]
    error_message: str
    raw_output: str