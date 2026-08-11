import logging
from collections.abc import Callable

from app.core.logger import logger
from app.tools.policy_tools import get_policy_details

ToolFunction = Callable[..., dict[str, object]]

AVAILABLE_TOOL_FUNCTIONS: dict[str, ToolFunction] = {
    "get_policy_details": get_policy_details,
}


def execute_tool(tool_name: str, arguments: dict[str, object])->dict[str, object]:
    logger.info(
        "Tool execution requested",
        extra={"tool_name": tool_name, "arguments": arguments},
    )
    tool_function= AVAILABLE_TOOL_FUNCTIONS.get(tool_name)

    if tool_function is None:
        logger.error("Tool execution failed: tool not allowed", extra={"tool_name": tool_name})
        return {
            "success": False,
            "error": f"Tool '{tool_name}' is not allowed.",
        }

    try:
        result = tool_function(**arguments)
        logger.info(
            "Tool execution completed",
            extra={"tool_name": tool_name, "result": result},
        )
        return {
            "success": True,
            "data": result,
        }
    except TypeError as exc:
        logger.exception("Tool execution failed due to invalid arguments", exc_info=exc)
        return {
            "success": False,
            "error": f"Invalid arguments for tool '{tool_name}': {exc}",
        }
    except Exception as exc:
        logger.exception("Tool execution failed", exc_info=exc)
        return {
            "success": False,
            "error": f"An error occurred while executing tool '{tool_name}'.",
        }
    