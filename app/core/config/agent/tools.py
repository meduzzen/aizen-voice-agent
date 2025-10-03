TOOLS_SALESBOT = [
    {
        "name": "get_service_details",
        "description": "Look up the firm's services, fees, and scope. Always call this before quoting fees or confirming scope.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "A short description of the client's matter (e.g. 'property settlement', 'employment contract review')",
                }
            },
            "additionalProperties": False,
            "required": ["query"],
        },
        "strict": True,
    },
]
