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
                "If the user says it's incorrect, ask again politely.",
                "After three unsuccessful attempts, ask them to spell their first name letter by letter.",
                "Once the correct first name is confirmed, proceed to the next state `2_get_last_name`.",
            ],
            examples=[
                "Before we continue, I'd love to know your first name to set things up for you.",
                "Did I get that right, John?",
                "Could you please spell your first name for me, letter by letter?"
            ],
            transitions=[
                Transition(next_step="2_get_last_name", condition="Once the correct first name is confirmed."),
                Transition(next_step="1_get_first_name_retry", condition="If the user says the name was heard incorrectly."),
                Transition(next_step="1_get_first_name_spelling", condition="If after 3 failed attempts, ask for spelling."),
            ],
        ),
        ConversationalState(
            id="1_get_first_name_retry",
            description="Retry getting the user's first name if previous attempt was unclear or incorrect.",
            instructions=[
                "Say politely: 'I'm sorry, could you please repeat your first name?'",
                "After the response, confirm again by repeating it back.",
                "If still unclear after 3 tries, ask them to spell it letter by letter."
            ],
            examples=[
                "I'm sorry, could you please repeat your first name?",
                "You said John, correct?",
                "I'm still having trouble understanding — could you please spell your first name letter by letter?"
            ],
            transitions=[
                Transition(next_step="2_get_last_name", condition="Once a valid and confirmed first name is obtained."),
                Transition(next_step="1_get_first_name_spelling", condition="After 3 unclear attempts."),
            ],
        ),
        ConversationalState(
            id="1_get_first_name_spelling",
            description="Ask the user to spell their first name letter by letter.",
            instructions=[
                "Say: 'No worries, could you please spell your first name for me, one letter at a time?'",
                "Repeat the letters back to confirm correctness.",
                "Once confirmed, proceed to asking for the last name."
            ],
            examples=[
                "No worries, could you please spell your first name for me, one letter at a time?",
                "You said J-O-H-N, correct?",
                "Got it — John. Thank you! Let's move on, what's your last name?"
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
                "If incorrect, ask again politely.",
                "After 3 failed attempts, ask the user to spell their last name letter by letter.",
            ],
            examples=[
                "Thank you! And may I have your last name as well?",
                "Did I get that right, Smith?",
                "Could you please spell your last name for me, letter by letter?"
            ],
            transitions=[
                Transition(next_step="3_get_and_verify_phone", condition="Once the correct last name is confirmed."),
                Transition(next_step="2_get_last_name_retry", condition="If user says the name was heard incorrectly."),
                Transition(next_step="2_get_last_name_spelling", condition="If 3 failed attempts to understand."),
            ],
        ),
        ConversationalState(
            id="1_get_last_name_retry",
            description="Retry getting the user's last name if previous attempt was unclear or incorrect.",
            instructions=[
                "Say politely: 'I'm sorry, could you please repeat your last name?'",
                "After the response, confirm again by repeating it back.",
                "If still unclear after 3 tries, ask them to spell it letter by letter."
            ],
            examples=[
                "I'm sorry, could you please repeat your last name?",
                "You said Smith, correct?",
                "I'm still having trouble understanding — could you please spell your last name letter by letter?"
            ],
            transitions=[
                Transition(next_step="3_get_and_verify_phone", condition="Once a valid and confirmed last name is obtained."),
                Transition(next_step="2_get_last_name_spelling", condition="After 3 unclear attempts."),
            ],
        ),
        ConversationalState(
            id="2_get_last_name_spelling",
            description="Ask the user to spell their last name letter by letter.",
            instructions=[
                "Say: 'Could you please spell your last name for me, one letter at a time?'",
                "Repeat the letters back to confirm correctness.",
                "Once confirmed, proceed to the next step."
            ],
            examples=[
                "Could you please spell your last name for me, one letter at a time?",
                "You said S-M-I-T-H, correct?",
                "Got it — Smith. Thank you! Let's move on."
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
                "After you asked the user about phone ALWAYS and IMMEDIATELY call the `wait_for` tool with **seconds: 10** to silently wait while the user says the full number. Do not tell the user you are waiting.",
                "Once you 15 seconds is over, IMMEDIATELY repeat the number back digit by digit and ALWAYS ask: 'You said [number], correct?'",
                "If the user says 'no' or indicates the number is incorrect, politely ask them to repeat the number. Always repeat only the most recent number provided by the user.",
                "Continue this loop until the user confirms the number is correct. Do not proceed until a valid phone number is confirmed."
                "You can move on to the next state ONLY if user confirms phone number."
                "After user confirms phone number, IMMEDIATELY go to next state `3_get_company_name`."
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
                "  2. IMMEDIATELY CALL `create_contact` tool with the summarized companyName",
                "  3. After contact is created, ALWAYS say: 'Perfect, thank you! Would you like to schedule an appointment?'",
                "  4. DO NOT END - immediately transition to state 5_get_appointment",
                "  5. If the contact already exists, tell the user and go to the next state.",
            ],
            examples=[
                "Could you please share your company name and briefly describe what your company does?",
                "What's your company name and what does your company do?",
                "After receiving: 'Perfect, thank you! Would you like to schedule an appointment?'",
                "If the contact already exists: 'Oh, it looks like you're already in our database, happy to see you again! Would you like to schedule a call with our team to discuss your project in detail?'",
            ],
            transitions=[
                Transition(
                    next_step="5_get_appointment",
                    condition="ALWAYS move to this state after contact is successfully created. This is MANDATORY.",
                ),
                Transition(next_step="4_get_company_name", condition="If invalid or empty company name input - ask again."),
            ],
        ),
        ConversationalState(
            id="5_get_appointment",
            description="Offer to schedule an appointment and gather details if user agrees.",
            instructions=[
                "IMPORTANT: You are now in the appointment scheduling state. This happens RIGHT AFTER contact creation.",
                "Start by politely asking the user if they would like to schedule an appointment with the Meduzzen team.",
                "Example: 'Would you like to schedule a call with our team to discuss your project in detail?'",
                "If they say YES:",
                "  1. CALL THE TOOL `get_free_appointment_slots` to retrieve currently available time slots.",
                "  2. Present ONLY the available options to the user in a friendly and natural way (for example, 'We have openings at 10:00, 11:30, and 15:00. Which one works best for you?').",
                "  3. Ask them to choose their preferred date and time.",
                "  4. Once they confirm a slot, CALL THE TOOL `create_appointment` with the details.",
                "  5. If the API responds that the selected slot is no longer available, politely inform the user (for example: 'Oh, it seems that time was just taken. Let me check the latest available times for you...'),",
                "     then CALL get_free_appointment_slots again to show updated available slots and let the user choose again.",
                "  6. When the appointment is successfully created, confirm it and thank the user.",
                "If they say NO:",
                "  1. Acknowledge politely: 'No problem! Feel free to reach out whenever you're ready.'",
                "  2. Offer alternative: 'Our team will contact you soon to follow up.'",
                "If their response is unclear, gently ask for clarification.",
                "After handling their response (yes or no), you may end the conversation naturally or ask if they have any other questions.",
            ],
            examples=[
                "Would you like to schedule a call with our team to discuss your project in detail?",
                "If yes: Great! Let me check our available slots... Here are some options: [show slots]. Which time works best for you?",
                "If slot unavailable: Oh, it looks like that time was just taken! Here are the new available times: [show updated slots].",
                "If no: No problem! Our team will reach out to you soon. Is there anything else I can help you with today?",
            ],
            transitions=[
                Transition(
                    next_step=None,
                    condition="After appointment is created OR user declines the appointment offer. Conversation can naturally conclude.",
                ),
                Transition(
                    next_step="5_get_appointment",
                    condition="If the user's response about appointment preferences is unclear - ask again for clarification.",
                ),
            ],
        ),
    ]
)
