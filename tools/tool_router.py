from tools.tools_registry import available_tools

def execute_tool(tool_name, arguments):
    
    tool = available_tools.get(tool_name)
    if not tool:
        raise LookupError(f"Tool: {tool_name} not found..")
    
    func = tool.function_reference
    result = func(**arguments)

    return result

