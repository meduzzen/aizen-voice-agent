from pydantic import BaseModel, Field


class ScenarioSchema(BaseModel):
    scenario_name: str = Field("Name of the scenario")


class ScenarioInstructions(BaseModel):
    opening: str
    discovery: str
    value_mapping: str
    closing: str
    objection_handling: str
    ending: str


class ScenarioTools(BaseModel):
    opening: list[str]
    discovery: list[str]
    value_mapping: list[str]
    closing: list[str]
    objection_handling: list[str]
    ending: list[str]


class ScenarioTransitions(BaseModel):
    opening: list[str]
    discovery: list[str]
    value_mapping: list[str]
    closing: list[str]
    objection_handling: list[str]
    ending: list[str]


class Scenario(BaseModel):
    states: list[str]
    instructions: ScenarioInstructions
    tools: ScenarioTools
    transitions: ScenarioTransitions
