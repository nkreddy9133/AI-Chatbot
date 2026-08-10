import json

from openai import AsyncOpenAI

from app.core.config import settings
from app.models.assistant import ToolExecution
from app.tools.tool_definitions import POLICY_TOOL_DEFINITION
from app.tools.tool_executor import execute_tool

class ToolAssistantService:
    def __init__(self) -> None:
        self.client = AsyncOpenAI(
            api_key=settings.openai_api_key
        )

        self.tools = [
            POLICY_TOOL_DEFINITION,
        ]

        self.instructions = (
            "You are a healthcare policy support support assistant working only with synthetic demonstration data. Use the available policy lookup funtion when the user asks for specific policy information. Never claim that synthetic data represents a real patient, member, employer, insure or policy. If a policy is not found, cleraly say so."
        )

    async def answer(
            self,
            message: str
    )-> tuple[str, list[ToolExecution]]:
        input_items: list[object]=[
            {
                "role": "user",
                "content": message,
            }
        ]

        tool_executions: list[ToolExecution]=[]

        response=await self.client.responses.create(
            model=settings.openai_model,
            instructions=self.instructions,
            tools=self.tools,
            tool_choice="auto",
            input=input_items
        )

        input_items.extend(response.output)

        function_calls=[
            item
            for item in response.output
            if item.type == "function_call"
        ]

        if not function_calls:
            return response.output_text, tool_executions

        for function_call in function_calls:
            arguments = json.loads(
                function_call.arguments
            )

            tool_result=execute_tool(
                tool_name=function_call.name,
                arguments=arguments)

            tool_executions.append(
                ToolExecution(
                    tool_name=function_call.name,
                    arguments=arguments,
                    result=tool_result
                    )
            )

            input_items.append(
                {
                "type": "function_call_output",
                "call_id": function_call.call_id,
                "output": json.dumps(tool_result)
                }
            )

        final_response=await self.client.responses.create(
            model=settings.openai_model,
            instructions=self.instructions,
            tools=self.tools,
            input=input_items
        )

        return(
            final_response.output_text,
            tool_executions
        )


tool_assistant_service=ToolAssistantService()

        