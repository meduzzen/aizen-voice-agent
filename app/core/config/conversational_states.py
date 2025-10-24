from app.schemas.conversational_states import (
    ConversationalState,
    ConversationFlow,
    Transition,
)

CONVERSATIONAL_STATES_WEBSALES_BOT = ConversationFlow(
    states=[
        ConversationalState(
            id="1_get_first_name",
            description="Ask for and confirm the user's first name.",
            instructions=[
                "Ask politely: 'Before we continue, I'd love to know your first name to set things up for you.'",
                "After the user responds, repeat what you heard — e.g., 'Did I get that right, [first_name]?'",
                "If the user says it's incorrect, ask to spell the name letter by letter.",
                "Once the correct first name is confirmed, proceed to the next state `2_get_last_name`.",
            ],
            examples=[
                "Before we continue, I'd love to know your first name to set things up for you.",
                "Did I get that right, John?",
                "Could you please spell your first name for me, letter by letter?",
            ],
            transitions=[
                Transition(next_step="2_get_last_name", condition="Once the correct first name is confirmed."),
                Transition(next_step="1_get_first_name_spelling", condition="If the first name is incorrect, ask for spelling."),
            ],
        ),
        ConversationalState(
            id="1_get_first_name_spelling",
            description="Ask the user to spell their first name letter by letter.",
            instructions=[
                "Say: 'Could you please spell your first name for me, one letter at a time?'",
                "Repeat the letters back to confirm correctness.",
                "Once confirmed, proceed to asking for the last name.",
            ],
            examples=[
                "Could you please spell your first name for me, one letter at a time?",
                "You said J-O-H-N, correct?",
                "Got it — John. Thank you! Let's move on, what's your last name?",
            ],
            transitions=[
                Transition(next_step="2_get_last_name", condition="Once the spelled first name is confirmed."),
            ],
        ),
        ConversationalState(
            id="2_get_last_name",
            description="Ask for and confirm the user's last name.",
            instructions=[
                "Politely say: 'Thank you! And may I have your last name as well?'",
                "After the response, confirm by repeating — e.g., 'Did I get that right, [last_name]?'",
                "If incorrect, ask to spell it letter by letter.",
                "Once the correct last name is confirmed, proceed to the next state `3_get_and_verify_phone`.",
            ],
            examples=[
                "Thank you! And may I have your last name as well?",
                "Did I get that right, Smith?",
                "Could you please spell your last name for me, letter by letter?",
            ],
            transitions=[
                Transition(next_step="3_get_and_verify_phone", condition="Once the correct last name is confirmed."),
                Transition(next_step="2_get_last_name_spelling", condition="If the last name is incorrect, ask for spelling."),
            ],
        ),
        ConversationalState(
            id="2_get_last_name_spelling",
            description="Ask the user to spell their last name letter by letter.",
            instructions=[
                "Say: 'Could you please spell your last name for me, one letter at a time?'",
                "Repeat the letters back to confirm correctness.",
                "Once confirmed, proceed to the next step.",
            ],
            examples=[
                "Could you please spell your last name for me, one letter at a time?",
                "You said S-M-I-T-H, correct?",
                "Got it — Smith. Thank you! Let's move on.",
            ],
            transitions=[
                Transition(next_step="3_get_and_verify_phone", condition="Once the spelled last name is confirmed."),
            ],
        ),
        ConversationalState(
            id="3_get_and_verify_phone",
            description="Request phone number including country code and verify by repeating it back.",
            instructions=[
                "Politely request the user's phone number, making sure they include the full international format (e.g., +380XXXXXXXXX). Ask the user to say each digit slowly and clearly, especially if digits repeat.",
                "After you asked the user about phone call the `wait_for` tool with **seconds: 3** to silently wait while the user says the full number. Do not tell the user you are waiting.",
                "Once waiting is over, call the `get_phone_number` tool with the user's transcript to extract and save the number.",
                "Once you 3 seconds is over, repeat the number back digit by digit and ALWAYS ask: 'You said [number], correct?'",
                "If the user says 'no' or indicates the number is incorrect, politely ask them to repeat the number. Always repeat only the most recent number provided by the user.",
                "If the user said 'yes' and confirms phone number, move to the next state `4_get_company_name` and NEVER call `get_phone_number` tool again."
                "Continue this loop until the user confirms the number is correct. Do not proceed until a valid phone number is confirmed."
                "You can move on to the next state ONLY if user confirms phone number."
                "After user confirms phone number, go to next step `4_get_company_name`.",
            ],
            examples=[
                "May I have your phone number in full international format, including the country code? For example: +380XXXXXXXXX.",
                "You said +380-67-123-4567, correct?",
                "User: No, that's not correct.",
                "You said +380-67-765-4321, correct?",
            ],
            transitions=[
                Transition(next_step="4_get_company_name", condition="Once a valid phone number is confirmed."),
                Transition(next_step="3_get_and_verify_phone", condition="If invalid, unclear, or rejected by the user."),
            ],
        ),
        ConversationalState(
            id="4_get_company_name",
            description="Ask for company name and brief description, summarize, create contact, then proceed to appointment.",
            instructions=[
                "Politely ask, 'Could you please share your company name and briefly describe what your company does?'",
                "Examples of what to expect:",
                "  - 'We're called Bright Homes and we're a real estate agency'",
                "  - 'Smith & Partners, we're a law firm focusing on corporate law'",
                "Do NOT verify or spell back the company name; just accept it.",
                "If the response is empty or unclear, politely ask again until a valid company name is received.",
                "Once you receive the company name and description:",
                "  1. Summarize into format: 'CompanyName - brief description' (max 10 words for description)",
                "  2. After you get CompanyName and description - call `create_contact` tool with the summarized companyName",
                "  3. DO NOT END - immediately transition to state 5_get_available_slots",
            ],
            examples=[
                "Could you please share your company name and briefly describe what your company does?",
                "What's your company name and what does your company do?",
                "After receiving: 'Perfect, thank you! Would you like to schedule an appointment?'",
            ],
            transitions=[
                Transition(
                    next_step="5_get_available_slots",
                    condition="ALWAYS move to this state after contact is successfully created. This is MANDATORY.",
                ),
                Transition(next_step="4_get_company_name", condition="If invalid or empty company name input - ask again."),
            ],
        ),
        ConversationalState(
            id="5_get_available_slots",
            description="Ask user for timezone, retrieve available slots, and present them in user's timezone.",
            instructions=[
                "Firstly, ALWAYS ask the user if they would like to schedule an appointment with the Meduzzen team. Don't ask about the timezones or slots, just find out if the user wants an appointment. NEVER call any tools until you know the user's response.",
                "If they say YES:",
                "  1. Ask the user in which city/timezone they are located.",
                "  2. Wait for timezone confirmation from user.",
                "  3. ONLY after receiving a timezone from the user, ALWAYS politely ask user to wait a little bit before you can get the available slots",
                "  4. CALL THE TOOL `get_free_appointment_slots` with the user's timezone.",
                "  5. AFTER receiving UTC slots from the API, CALL THE TOOL `convert_time` to convert each slot into the user's local time before presenting them.",
                "  6. Immediately after receiving free slots, present them in a friendly way (e.g., 'We have openings at 10:00, 11:30, and 15:00. Which one works best for you?').",
                "  7. Ask the user to select one of the available times.",
                "If they say NO:",
                "  1. Acknowledge politely: 'No problem! Feel free to reach out whenever you're ready.'",
                "If their response is unclear, gently ask for clarification.",
            ],
            examples=[
                "Would you like to schedule a call with our team to discuss your project in detail?",
                "Please tell me which city or country you are in so that I can select free slots for your local time.",
                "After timezone: Please wait a moment so I can check our available times for you...",
                "Perfect! Here are our available times: 10:00, 11:30, 15:00. Which works best for you?",
                "If no: No problem! Feel free to reach out whenever you're ready.",
            ],
            transitions=[
                Transition(
                    next_step="6_create_appointment",
                    condition="After user selects a specific time slot.",
                ),
                Transition(
                    next_step=None,
                    condition="If user declines appointment offer.",
                ),
                Transition(
                    next_step="5_get_available_slots",
                    condition="If user's timezone choice or slot selection is unclear - ask again.",
                ),
            ],
        ),
        ConversationalState(
            id="6_create_appointment",
            description="Confirm selected time, create the appointment, and handle conflicts.",
            instructions=[
                "Confirm the user's selected time slot.",
                "CALL THE TOOL `convert_time` if the selected time is in local timezone to convert it into ISO8601 format with correct timezone offset for GoHighLevel.",
                "CALL THE TOOL `create_appointment` with the appointment details.",
                "If the slot is no longer available:",
                "  1. Politely inform the user: 'Oh, it seems that time was just taken. Let me check the latest available times for you...'",
                "  2. TRANSITION back to `5_get_available_slots` to show updated slots.",
                "If the appointment is successfully created:",
                "  1. Confirm the booking with all details.",
                "  2. Thank the user.",
                "  3. Ask if there's anything else you can help with or naturally conclude the conversation.",
            ],
            examples=[
                "Perfect! Let me book 11:30 for you...",
                "If slot unavailable: Oh, it looks like that time was just taken! Let me show you the updated available times...",
                "Appointment confirmed for tomorrow at 11:30. Thank you, we look forward to speaking with you!",
            ],
            transitions=[
                Transition(
                    next_step=None,
                    condition="After appointment is successfully created.",
                ),
                Transition(
                    next_step="5_get_available_slots",
                    condition="If the selected slot is no longer available - show updated slots.",
                ),
            ],
        ),
    ],
)
