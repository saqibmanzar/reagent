from tools.tools_registry import available_tools

def build_tool_prompt():
    tool_prompt: str = 'You have access to the following tools that can help you solve tasks.: \n'
    for tool_name, tool_data in available_tools.items():
        tool_prompt += f"Tool: " + str(tool_name) + '\n'
        tool_prompt += "Description: " + str(tool_data.description) + '\n\n'
        tool_prompt += "Arguments: \n"
        tool_prompt += "{\n" 
         
        properties = tool_data.input_schema.get("properties", {}) 
        arg_lines = []
        for arg_name, arg_info in properties.items():
            arg_type = arg_info.get("type", "string")
            arg_lines.append(f'  "{arg_name}": "{arg_type}"')

        tool_prompt += ",\n".join(arg_lines)
        tool_prompt += "\n}\n\n"

        required = tool_data.input_schema.get("required", []) 
        tool_prompt += "Required Arguments:\n"
        for req_arg in required:
            tool_prompt += f"- {req_arg}\n"

        tool_prompt += "\n\n"

    tool_prompt += """\n
You are an agent that performs exactly one action per step:

1. Call a tool
2. Return a final answer

You MUST respond in valid JSON with one of these types:
- "tool_call"
- "final_answer"

Rules:
- Always include "type"
- Do NOT output anything outside JSON
- Use only provided tools
- Do NOT guess tool arguments
- Use tools when required (e.g., calculations)
- Always end code with print() to output the final result
- If a tool returns a result starting with "Code execution failed", fix the code and retry. Never give a final answer based on a failed tool call.

Formats:

Tool call:
{
  "type": "tool_call",
  "tool": "<tool_name>",
  "arguments": { ... }
}

Final answer:
{
  "type": "final_answer",
  "final_answer": "<concise answer>",
  "explanation": "<optional short explanation>"
}

For "final_answer":
- "answer" = direct, concise output
- "explanation" = optional (only if user asks why/how)
- No step-by-step reasoning

Always return valid JSON.
    """
    return tool_prompt