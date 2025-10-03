from pydantic import BaseModel


class GetClientSchema(BaseModel):
    full_name: str
    phone_number: str
    company_name: str
    company_description: str
