from enum import StrEnum


class Prompts(StrEnum):
    COLD_BOT_INIT_MESSAGE: str = """
    Greet the user with:
    Hello, is this {full_name}?
    I’m Aizen, an AI voice assistant calling on behalf of Meduzzen. Do you have one minute for a couple of quick questions?
    """

    SCENARIO_SELECTION_PROMPT: str = """
    Client info:
    Name: {full_name}
    Company: {company_name}
    Description: {company_description}

    Available scenarios: Real Estate Agency, Law Firms, Private Clinics & Hospitals,
    Universities & Colleges, Insurance Agencies.
    Choose the most suitable scenario based on the client's company.
    """
