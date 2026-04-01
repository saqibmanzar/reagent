from llm.ollama_client import call_llm
from agent.response_parser import parse_llm_response
from memory_manager.memory import fetch_memory, update_session
from tools.tool_router import execute_tool
from observability.langfuse_client import langfuse


MAX_STEPS = 6


async def react_loop(id, model, message, system=None, params=None):
    memory = fetch_memory(id, message, system)

    history_message = memory.get("history")
    chat_history = memory.get("chat")
    messages = memory.get("messages")
    system_prompt = memory.get("system")

    final_answer = None

    for step in range(MAX_STEPS):
        with langfuse.start_as_current_observation(
            name=f"agent_step",
            as_type="span",
            input={
                "step": step,
                "history_length": len(history_message)
            }
        ):

            with langfuse.start_as_current_observation(
                name="llm_call",
                as_type="generation",
                input={"messages": history_message, "model": model, "step": step}
            ) as span:

                raw_output = await call_llm(history_message, model, params)
                span.update(output={"raw_output": raw_output})

            with langfuse.start_as_current_observation(
                name="parser",
                as_type="span",
                input={"raw_output": raw_output, "step": step}
            ) as span:

                parsed_response = parse_llm_response(raw_output)
                span.update(output={"type": parsed_response.type})

            if parsed_response.type == "error":
                with langfuse.start_as_current_observation(
                    name="error",
                    as_type="span",
                    input={"raw_output": raw_output, "step": step}
                ) as error_span:

                    error_span.update(output={
                        "error": parsed_response.error_message
                    })
                return parsed_response

            elif parsed_response.type == "tool_call":
                tool = parsed_response.tool
                arguments = parsed_response.arguments

                history_message.append({
                    "role": "assistant",
                    "content": raw_output
                })

                with langfuse.start_as_current_observation(
                    name="tool_execution",
                    as_type="tool",
                    input={"tool": tool, "arguments": arguments, "step": step}
                ) as span:
                    try:
                        result = execute_tool(tool, arguments)
                        span.update(output={
                            "result": str(result),
                            "status": "success"
                        })
                    except Exception as e:
                        span.update(output={
                            "error": str(e),
                            "status": "failed"
                        })
                        return {
                            "type": "error",
                            "error_message": f"Tool execution failed: {str(e)}",
                            "raw_output": raw_output
                        }

                tool_message = f"Tool: {tool}\nArguments: {arguments}\nResult: {result}"

                history_message.append({
                    "role": "tool",
                    "content": tool_message
                })

                print("History: ", history_message)

            elif parsed_response.type == "final_answer":
                final_answer = f'Answer: {parsed_response.final_answer}.' + f' Explanation: {parsed_response.explanation}'
                with langfuse.start_as_current_observation(
                    name="final_answer",
                    as_type="span",
                    input={"step": step}
                ) as final_span:

                    final_answer = f'Answer: {parsed_response.final_answer}.' + f' Explanation: {parsed_response.explanation}'

                    final_span.update(output={
                        "final_answer": parsed_response.final_answer
                    })

                history_message.append({
                    "role": "assistant",
                    "content": final_answer
                })
                print("History: ", history_message)

                break

    else:
        with langfuse.start_as_current_observation(
            name="max_steps_exceeded",
            as_type="span"
        ) as span:
            span.update(output={"last_output": raw_output})
        return {
            "type": "error",
            "error_message": "Max steps exceeded",
            "raw_output": raw_output
        }

    update_session(id, chat_history, messages, final_answer, system_prompt)

    return final_answer