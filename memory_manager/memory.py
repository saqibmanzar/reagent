from prompts.system_prompt_builder import build_system_prompt

session_history = {}
HISTORY = -10


def fetch_memory(id, message, system=None):
    messages = []
    chat_history = []

    if id in session_history:
        chat_history = session_history.get(id)["message"]
        
    base_prompt = prompt_construction(id, system)
    system_prompt = build_system_prompt(base_prompt)
    messages.append({'role': 'user','content': message})
    history_message = chat_history[HISTORY:] + messages
    history_message = [{"role": "system", "content": system_prompt}] + history_message

    return {
        "history": history_message,
        "chat": chat_history,
        "messages": messages,
        "system": system_prompt
    }


def prompt_construction(id, system):
    system_prompt = '' 

    if id in session_history:
        system_prompt = session_history.get(id)["system"]        
    
    if system:
        system_prompt = system

    if not system_prompt:
        system_prompt = 'You are an AI assistant that can solve problems.\n'
    
    return system_prompt


def update_session(id, chat_history, messages, response, system_prompt):
    chat_history.extend(messages)
    chat_history.append({"role": "assistant", "content": response})
    session_history[id] = {"message": chat_history, "system": system_prompt}
    print("-------- Memory Updated -----------")