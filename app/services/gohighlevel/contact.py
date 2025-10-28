from pydantic import ValidationError

from app.core.config.config import settings
from app.core.config.enums import GoHighLevel
from app.schemas.gohighlevel.contact import (
    ContactBase,
    ContactDetail,
    ContactDetailResponse,
    ContactUpdate,
    CreateContactRequest,
    CustomFieldSchema,
)
from app.services.gohighlevel.gohighlevel import GoHighLevelService


class Contact(GoHighLevelService):
    def __init__(self):
        super().__init__()

    async def create_contact(
        self,
        firstName: str,
        lastName: str,
        phone: str,
        companyName: str,
        tags: list[GoHighLevel] = [GoHighLevel.FROM_AIZEN],
        customFields: list[CustomFieldSchema] | None = None,
        *args,
        **kwargs,
    ):
        try:
            request = CreateContactRequest(
                firstName=firstName,
                lastName=lastName,
                phone=phone,
                companyName=companyName,
            )
        except ValidationError as exc:
            error_msg = repr(exc.errors()[0]["type"])
            self.log(f"[CONTACT] Validation Error: {error_msg}")
            return {"error": error_msg}

        if customFields is None:
            customFields = [
                CustomFieldSchema(
                    id=settings.gohighlevel.CUSTOM_FIELDS_ID,
                    key=settings.gohighlevel.CUSTOM_FIELDS_KEY,
                    field_value="Conversation will be added here after the call ends.",
                )
            ]

        payload = ContactBase(
            firstName=request.firstName,
            lastName=request.lastName,
            phone=request.phone,
            companyName=request.companyName,
            tags=tags,
            customFields=customFields,
        ).model_dump(by_alias=True, exclude_none=True)

        payload["locationId"] = settings.gohighlevel.LOCATION_ID

        self.log(f"[CONTACT] Payload being sent: {payload}")

        response_json, status_code, text = await self.send_request("POST", "/contacts/", payload, return_status=True)

        self.log(f"[CONTACT] Create response ({status_code}): {text[:1000]}")

        if status_code >= 400:
            self.log(f"Failed to create contact ({status_code}): {response_json}")

            is_duplicate = False
            existing_contact_id = None

            if isinstance(response_json, dict):
                error_message = response_json.get("message", "").lower()
                if "does not allow duplicated contacts" in error_message or "duplicate" in error_message:
                    is_duplicate = True
                    meta = response_json.get("meta", {})
                    existing_contact_id = meta.get("contactId")
                    self.log(f"Contact with {phone} already exists (id: {existing_contact_id})")

            return {
                "is_duplicate": is_duplicate,
                "existing_contact_id": existing_contact_id,
            }

        contact_info = response_json.get("contact", {})
        self.log(f"Contact info: {contact_info}")

        contact_model = ContactDetail(**contact_info).model_dump()
        return {
            "is_duplicate": False,
            "contact_id": contact_model.get("contact_id"),
        }

    async def update_contact(
        self,
        contact_id: str,
        firstName: str | None = None,
        lastName: str | None = None,
        phone: str | None = None,
        companyName: str | None = None,
        tags: list[GoHighLevel] | None = None,
        customFields: list[CustomFieldSchema] | None = None,
        *args,
        **kwargs,
    ):
        payload = ContactUpdate(
            firstName=firstName, lastName=lastName, phone=phone, companyName=companyName, tags=tags, customFields=customFields
        ).model_dump(exclude_none=True)
        data = await self.send_request("PUT", f"/contacts/{contact_id}", payload, self.headers)
        self.log(f"Contact updated: {data}")

    async def delete_contact(self, contact_id: str):
        data = await self.send_request("DELETE", f"/contacts/{contact_id}", headers=self.headers)
        self.log(f"Contact deleted: {data}")
        
    async def get_contact(self, contact_id: str) -> ContactDetailResponse:
        data = await self.send_request("GET", f"/contacts/{contact_id}", headers=self.headers)
        self.log(f"Contact retrieved: {data}")

        contact_data = data.get("contact", {}) if isinstance(data, dict) else {}

        return ContactDetailResponse(**contact_data)
