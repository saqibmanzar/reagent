from pydantic import BaseModel
from typing import Callable, Any

class ToolSchema(BaseModel):
    name: str
    description: str
    input_schema: dict[str, Any]
    function_reference: Callable


