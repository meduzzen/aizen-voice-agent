from app.schemas.conversational_states import ConversationFlow, ConversationalState, Transition

CONVERSATIONAL_STATES_WEBSALES_BOT = ConversationFlow(
    states=[
        ConversationalState(
            id="1_get_first_name",
            description="Ask for the user's first name.",
            instructions=[
                "Politely ask, 'Before we continue, I'd love to know your first name to set things up for you.'",
                "Do NOT verify or spell back the name; just accept it.",
                "If the response is unrecognizable, politely ask again until a valid first name is received."
            ],
            examples=[
                "Before we continue, I'd love to know your first name to set things up for you."
            ],
            transitions=[
                Transition(
                    next_step="2_get_last_name",
                    condition="Once a valid first name is obtained."
                ),
                Transition(
                    next_step="1_get_first_name",
                    condition="If invalid, or unclear input."
                )
            ]
        ),
        ConversationalState(
            id="2_get_last_name",
            description="Ask for the user's last name.",
            instructions=[
                "Politely ask, 'Thank you! And may I have your last name as well?'",
                "Do NOT verify or spell back the name; just accept it.",
                "If the response is unrecognizable, politely ask again until a valid last name is received."
            ],
            examples=[
                "Thank you! And may I have your last name as well?"
            ],
            transitions=[
                Transition(
                    next_step="3_get_and_verify_phone",
                    condition="Once a valid last name is obtained."
                ),
                Transition(
                    next_step="2_get_last_name",
                    condition="If invalid or unclear input."
                )
            ]
        ),
        ConversationalState(
            id="3_get_and_verify_phone",
            description="Request phone number including country code and verify by repeating it back.",
            instructions=[
                "Politely request the user's phone number, making sure they include the full international format (e.g., +380XXXXXXXXX), also ALWAYS ask the user to say each digit slowly and clearly, especially if digits repeat.",
                "Once provided, repeat the number back digit by digit and ask: 'You said [number], correct?'",
                "If the user says 'no' or indicates the number is incorrect, politely ask them to repeat the number.",
                "Always repeat the most recent number provided by the user, not any previous attempts.",
                "Continue this loop until the user confirms the number is correct.",
                "Do not proceed until a valid phone number is confirmed."
            ],
            examples=[
                "May I have your phone number in full international format, including the country code? For example: +380XXXXXXXXX.",
                "You said +380-67-123-4567, correct?",
                "User: No, that's not correct.",
                "You said +380-67-765-4321, correct?"
            ],
            transitions=[
                Transition(
                    next_step="4_get_company_name",
                    condition="Once a valid phone number is confirmed."
                ),
                Transition(
                    next_step="3_get_and_verify_phone",
                    condition="If invalid, unclear, or rejected by the user."
                )
            ]
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
                "  4. DO NOT END - immediately transition to state 5_get_appointment"
            ],
            examples=[
                "Could you please share your company name and briefly describe what your company does?",
                "What's your company name and what does your company do?",
                "After receiving: 'Perfect, thank you! Would you like to schedule an appointment?'"
            ],
            transitions=[
                Transition(
                    next_step="5_get_appointment",
                    condition="ALWAYS move to this state after contact is successfully created. This is MANDATORY."
                ),
                Transition(
                    next_step="4_get_company_name",
                    condition="If invalid or empty company name input - ask again."
                )
            ]
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
                "After handling their response (yes or no), you may end the conversation naturally or ask if they have any other questions."
            ],
            examples=[
                "Would you like to schedule a call with our team to discuss your project in detail?",
                "If yes: Great! Let me check our available slots... Here are some options: [show slots]. Which time works best for you?",
                "If slot unavailable: Oh, it looks like that time was just taken! Here are the new available times: [show updated slots].",
                "If no: No problem! Our team will reach out to you soon. Is there anything else I can help you with today?"
            ],
            transitions=[
                Transition(
                    next_step=None,
                    condition="After appointment is created OR user declines the appointment offer. Conversation can naturally conclude."
                ),
                Transition(
                    next_step="5_get_appointment",
                    condition="If the user's response about appointment preferences is unclear - ask again for clarification."
                )
            ]
        )
    ]
)
