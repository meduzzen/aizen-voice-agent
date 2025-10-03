from pydantic import BaseModel, Field


class ScenarioSchema(BaseModel):
    scenario_name: str = Field("Name of the scenario")
