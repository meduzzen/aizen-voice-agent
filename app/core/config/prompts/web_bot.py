from enum import StrEnum


class Prompts(StrEnum):
    SUMMARIZATION_PROMPT: str = """
    You are a professional assistant for a law firm.
    Summarize the following phone call transcript clearly and concisely.
    Extract and present the following information:
     - Client's full name (if mentioned; if not, note "Not provided").
     - Reason for the call / matter (e.g., legal issue, consultation request, case follow-up).
     - All details shared during the conversation relevant to the matter (include dates, names, locations, and any legal context provided).

    Output the result in this JSON format:
        {
          "client_name": "",
          "matter": "",
          "details": "",
        }
    If any field is unknown, write "Not provided".
    Be factual and avoid adding information not stated in the transcript.
    """
    
    TOOL_RESULT_INSTRUCTION: str = """
    [Insert a natural short pause, as if checking notes, before responding.]
    Use {response_text} only as internal context — never expose it directly.
    Respond with one short confirmation sentence only.
    Do not provide details unless the user specifically asks.
    """

    WAIT_FOR_PHONE_INSTRUCTION = """
    [Insert a short silent pause as if listening to the user.]
    Use {response_text} only as internal context — never expose it directly.

    Just stay silent for 3 seconds while the user is speaking.
    """

    GET_PHONE_NUMBER_INSTRUCTION: str = """
    [Insert a natural short pause]
    IMPORTANT: The user said a phone number. Extract the EXACT digits they said, character by character.
    Do NOT interpret, do NOT add country codes, do NOT reformat.
    Save the exact number as spoken. BUT if the user says a phone number without a +, add a + at the beginning.
    Then ask: 'You said [exact_number], correct?'
    If confirmed -> next state: `4_check_company_memory`
    If 'no' -> ask again
    """
    
    EXTRACT_CONTACT_INFO: str = """
    Extract contact information from this call transcript.

    TRANSCRIPT:
    {formatted_transcript}

    EXTRACTION RULES:

    For firstName and lastName:
    - Extract ONLY if explicitly CONFIRMED by the user
    - User must have confirmed by saying "Yes", repeating it back, or correcting themselves
    - If mentioned multiple times, use the LAST confirmed version
    - Do NOT include unconfirmed mentions

    For phone:
    - Extract ONLY if explicitly CONFIRMED by the user
    - User must have confirmed by saying "Yes" or repeating the number back
    - If mentioned multiple times, use the LAST confirmed version
    - Do NOT include unconfirmed mentions

    For companyName:
    - Extract ANY mention of company name and description
    - No confirmation needed - if user said it, use it
    - If mentioned multiple times, use the LAST mention
    - Include company name + brief description of what they do

    IMPORTANT:
    - ALL FIELDS MUST BE FILLED
    - For name and phone: only confirmed versions
    - For company: any mention is fine

    Return: firstName, lastName, phone, companyName
    """
    
    GET_SERVICE_DETAILS_INSTRUCTION = """
    [Insert a natural short pause, as if checking notes, before responding.]

    You have a context, use this to answer to user's questions.

    You have received detailed information about our services in the function output above.
    Based on that information:
    Provide a brief, friendly summary (2-3 sentences maximum)
    Respond with 1-2 confirmation sentences.
    Do not provide details unless the user specifically asks.
    Example: "We offer various services including software development, consulting, and more. What would you like to know?"

    Context: {response_text}
    """

    CREATE_CONTACT_INSTRUCTION: str = """
    [Insert a natural short pause, as if checking notes, before responding.]

    Contact created successfully. Use {response_text} only as internal context — never expose it directly.

    If the response contains "error" or "is required":
      - Politely explain to the user that the field from the error is mandatory and without it, you will not be able to save the user to the database and book a call.
      - Ask him again to say the missing field.

    # CURRENT STATE TRANSITION: 4_check_company_memory or 5_ask_company_name -> 6_get_available_slots

    YOU MUST NOW PROCEED TO STATE "6_get_available_slots" and ask the user if they would like to schedule an appointment with the Meduzzen team. You should NEVER go straight to search available slots after creating contact. ALWAYS ask first if the user wants this appointment.

    Duplicate text: {duplicate_text}
    """
    
    GET_SLOTS_INSTRUCTION: str = """
    [Insert a natural short pause, as if checking the calendar, before responding.]

    IMPORTANT:
    - The `get_free_appointment_slots` tool automatically searches for available slots AND converts them to the user's local timezone.
    - If the timezone is not clear, politely ask for clarification.
    - Present the available time slots in the user's local time in a friendly way.
    - List 3-5 options and ask them to choose.
    - Handle errors gracefully: if slot retrieval or conversion fails, inform the user politely and ask them to try again.

    EXAMPLE:
    User: "I am in New York."
    Tool returns: "[2025-10-22T10:00:00-04:00, 2025-10-22T11:00:00-04:00]" (already converted to NY timezone)
    LLM response: "Perfect! We have openings October 22nd at 10:00 AM and 11:00 AM in your local time. Which one works best for you?"

    Friendly response example:
    "I have openings tomorrow at 10:00, 13:00, and 16:00 your local time. Which works best for you?"

    CONTEXT:
    {response_text}
    """

    CREATE_APPOINTMENT_INSTRUCTION: str = """
    [Insert a natural short pause, as if confirming the booking, before responding.]

    Response from booking system: {response_text}

    YOUR INSTRUCTIONS:
    If the response contains "Slot unavailable", "Error", or indicates failure:
      - Apologize politely to the user
      - Explain that the selected time slot is no longer available
      - Offer to show updated available times
      - Ask: "Would you like me to check what times are available now?"

    Example: "Oh, I'm sorry! It looks like that time slot was just booked by someone else. Would you like me to show you the latest available times?"

    If the response is successful (contains appointment details like appointmentId):
      - Thank them for scheduling
      - Confirm the date and time in their local timezone (use `convert_time` if needed)
      - Let them know the team will contact them
      - Ask if there's anything else you can help with

    Example: "Perfect! I've scheduled your call for tomorrow at 2:00 PM Toronto time. Our team will reach out to you shortly. Is there anything else I can help you with?"
    """
