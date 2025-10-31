TOOLS_SALESBOT = [
    {
        "name": "get_service_details",
        "description": "Look up the firm's services, fees, and scope. Always call this before quoting fees or confirming scope.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "A short description of the client's matter",
                }
            },
            "additionalProperties": False,
            "required": ["query"],
        },
        "strict": True,
    },
    {
        "name": "wait_for",
        "description": "Pauses the conversation for a given number of seconds before resuming. Use this to silently wait while the user says the full phone number.",
        "parameters": {
            "type": "object",
            "properties": {"seconds": {"type": "integer", "description": "The number of seconds to wait."}},
            "additionalProperties": False,
            "required": ["seconds"],
        },
        "strict": True,
    },
    {
        "name": "get_phone_number",
        "description": "Fetches the last saved user transcript containing a phone number in international format.",
        "parameters": {
            "type": "object",
            "properties": {
                "transcript": {
                    "type": "string",
                    "description": "The user transcript that should contain the phone number.",
                }
            },
            "additionalProperties": False,
            "required": ["transcript"],
        },
        "strict": True,
    },
    {
        "name": "create_contact",
        "description": "Creates a new contact record in the CRM system. The contact will automatically have a custom field for storing the conversation transcript.",
        "parameters": {
            "type": "object",
            "properties": {},
            "additionalProperties": False,
            "required": [],
        },
        "strict": True,
    },
    {
        "name": "update_contact_info",
        "description": "Updates an existing contact record in the CRM system.",
        "parameters": {
            "type": "object",
            "properties": {
                "contact_id": {"type": "string", "description": "The unique ID of the contact."},
                "tags": {"type": "array", "description": "Updated tags for contact.", "items": {"type": "string"}},
                "customFields": {
                    "type": "array",
                    "description": "Updated list of custom fields for this contact. Usually used to update the transcript text.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string", "description": "Unique ID of the custom field."},
                            "key": {"type": "string", "description": "Updated custom field key"},
                            "field_value": {
                                "type": "string",
                                "description": "New value for this custom field, e.g. the conversation transcript.",
                            },
                        },
                        "required": ["id", "key", "field_value"],
                    },
                },
            },
            "additionalProperties": False,
            "required": ["contact_id"],
        },
        "strict": True,
    },
    {
        "name": "get_free_appointment_slots",
        "description": "Retrieve available free appointment slots for a given date range and convert them to the user's local timezone.",
        "parameters": {
            "type": "object",
            "properties": {
                "startDate": {
                    "type": "string",
                    "description": "Start date (ISO format) for the search."
                },
                "endDate": {
                    "type": "string",
                    "description": "End date (ISO format) for the search."
                },
                "timezone": {
                    "type": "string",
                    "description": "User's timezone (e.g., 'America/New_York', 'Europe/London'). Slots will be converted to this timezone."
                },
            },
            "additionalProperties": False,
            "required": ["startDate", "endDate", "timezone"],
        },
        "strict": True,
    },
    {
        "name": "create_appointment",
        "description": "Creates a new appointment in the specified calendar for a contact. Automatically converts time to ISO 8601 format.",
        "parameters": {
            "type": "object",
            "properties": {
                "startTime": {
                    "type": "string",
                    "description": "Appointment start time (ISO 8601 format with timezone, e.g., '2025-11-03T13:00:00-04:00')"
                },
                "timezone": {
                    "type": "string",
                    "description": "User's timezone if time needs conversion (e.g., 'America/Toronto', 'Europe/London')."
                },
            },
            "additionalProperties": False,
            "required": ["startTime"],
        },
        "strict": True,
    },
    {
        "name": "update_appointment",
        "description": "Updates an existing appointment's details.",
        "parameters": {
            "type": "object",
            "properties": {
                "appointment_id": {"type": "string", "description": "The unique ID of the appointment."},
                "calendarId": {"type": "string", "description": "The calendar ID."},
                "contactId": {"type": "string", "description": "The contact ID."},
                "startTime": {"type": "string", "description": "Updated start time (ISO format)."},
                "endTime": {"type": "string", "description": "Updated end time (ISO format)."},
                "title": {
                    "type": "string",
                    "description": "Updated title of appointment. Should be named as 'Client's name + [Scheduled by Sales Bot]'",
                },
            },
            "additionalProperties": False,
            "required": ["appointment_id", "calendarId", "contactId"],
        },
        "strict": True,
    },
]
