from agent.models import ToolCall, FinalAnswer, ResponseError
import re
from pydantic import ValidationError
import json

def extract_json(raw_output):
    match = re.search(r'\{.*\}', raw_output, re.DOTALL)
    if not match:
        raise ValueError("No JSON Found in LLM Response")
    
    return match.group(0)


def parse_llm_response(raw_output: str):
    try:
        json_str = extract_json(raw_output)
    except Exception as e:
        return ResponseError(
            type="error",
            error_message=f"Error in parsing json: {e}",
            raw_output=raw_output
        )
    
    try:
        data = json.loads(json_str)
    except Exception as e:
        return ResponseError(
            type="error",
            error_message=f"Failed to extract json: {e}",
            raw_output=raw_output
        )

    response_type = data.get("type")
    if not response_type:
        return ResponseError(
            type="error",
            error_message="Missing 'type' field",
            raw_output=raw_output
        )
    
    try:
        if response_type == 'tool_call':
            return ToolCall(**data)
        elif response_type == 'final_answer':
            return FinalAnswer(**data)
        else:
            return ResponseError(
                type="error",
                error_message=f"Unknown type: {response_type}",
                raw_output=raw_output
            )
    except ValidationError as e:
        return ResponseError(
            type="error",
            error_message=f"Schema validation failed: {str(e)}",
            raw_output=raw_output
        )
