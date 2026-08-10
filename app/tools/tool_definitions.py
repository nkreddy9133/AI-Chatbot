POLICY_TOOL_DEFINITION: dict[str, object] = {
    "type": "function",
    "name": "get_policy_details",
    "description": "Retrieves details of a policy based on the provided policy ID. Look up details for a synthetic healthcare policy using its policy identifier. Use this when the user asks about policy status, plan type, dates, or deductible information.",
    "parameters": {
        "type": "object",
        "properties": {
            "policy_id": {
                "type": "string",
                "description": "The unique identifier of the policy to look up."
            }
        },
        "required": ["policy_id"],
        "additionalProperties": False
    },
    "strict": True
}