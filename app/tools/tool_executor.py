from collections.abc import Callable

from app.tools.policy_tools import get_policy_details

ToolFunction = Callable[..., dict[str, object]]

AVAILABLE_TOOL_FUNCTIONS: dict[str, ToolFunction] = {
    "get_policy_details": get_policy_details,
}

def execute_tool(tool_name: str, arguments: dict[str, object])->dict[str, object]:
    tool_function= AVAILABLE_TOOL_FUNCTIONS.get(tool_name)

    if tool_function is None:
        return {
            "success": False,
            "error": f"Tool '{tool_name}' is not allowed.",
        }

    try:
        result = tool_function(**arguments)

        return {
            "success": True,
            "data": result,
        }
    except TypeError as exc:
        return {
            "success": False,
            "error": f"Invalid arguments for tool '{tool_name}': {exc}",
        }
    except Exception:
        return {
            "success": False,
            "error": f"An error occurred while executing tool '{tool_name}'.",
        }
    