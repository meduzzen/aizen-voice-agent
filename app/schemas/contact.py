from pydantic import BaseModel, Field


class ContactSchema(BaseModel):
    firstName: str = Field(..., description="First name of the contact")
    lastName: str = Field(..., description="Last name of the contact")
    phone: str = Field(..., description="Phone number of the contact")
    companyName: str = Field(..., description="Company name and its brief description of the contact")