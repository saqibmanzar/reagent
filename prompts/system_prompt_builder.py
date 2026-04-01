from prompts.tool_prompt_builder import build_tool_prompt

def build_system_prompt(system: str):
    final_prompt = build_tool_prompt()
    final_prompt = system + '\n\n' + final_prompt
    
    return final_prompt


