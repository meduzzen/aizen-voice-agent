from pydantic import BaseModel, Field


class Transition(BaseModel):
    next_step: str | None = Field(
        None, description="ID of the next step in the conversation."
    )
    condition: str = Field(..., description="Condition that triggers the transition.")


class ConversationalState(BaseModel):
    id: str = Field(..., description="Unique identifier for the state.")
    description: str = Field(..., description="Brief explanation of the state's purpose.")
    instructions: list[str] = Field(..., description="Step-by-step instructions.")
    examples: list[str] = Field(..., description="Sample responses.")
    transitions: list[Transition] = Field(..., description="Possible next states.")


class ConversationFlow(BaseModel):
    states: list[ConversationalState] = Field(..., description="All conversation states in sequence.")
    