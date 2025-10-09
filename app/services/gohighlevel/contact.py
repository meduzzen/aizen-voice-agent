from app.core.config.config import settings
from app.core.config.enums import GoHighLevel
from app.schemas.gohighlevel.contact import ContactBase, ContactDetail, ContactUpdate, CustomFieldSchema
from app.services.gohighlevel.gohighlevel import GoHighLevelService


class Contact(GoHighLevelService):
    def __init__(self):
        super().__init__()

    async def create_contact(self, firstName: str, lastName: str, phone: str, companyName: str, tags: list[GoHighLevel] = [GoHighLevel.FROM_AIZEN], customFields: list[CustomFieldSchema] | None = None):
        if customFields is None:
            customFields = [
                CustomFieldSchema(
                    id=settings.gohighlevel.CUSTOM_FIELDS_ID,
                    key=settings.gohighlevel.CUSTOM_FIELDS_KEY,
                    field_value="Conversation will be added here after the call ends."
                )
            ]

        payload = ContactBase(firstName=firstName, lastName=lastName, phone=phone, companyName=companyName,
                              tags=tags, customFields=customFields).model_dump(by_alias=True, exclude_none=True)

        payload["locationId"] = settings.gohighlevel.LOCATION_ID

        self.log(f"[CONTACT] Payload being sent: {payload}")

        response_json, status_code, text = await self.send_request("POST", "/contacts/", payload, return_status=True)

        self.log(f"[CONTACT] Create response ({status_code}): {text[:1000]}")

        if status_code >= 400:
            self.log(
                f"[ERROR] Failed to create contact: {response_json}", error=True)
            return None

        contact_info = response_json.get("contact", {})
        self.log(f"[CONTACT] Parsed contact info: {contact_info}")

        if not contact_info:
            self.log("[ERROR] Empty contact data in GHL response", error=True)
            return None

        contact_model = ContactDetail(**contact_info).model_dump()
        return contact_model
    
    async def update_contact(
        self,
        contact_id: str,
        firstName: str | None = None,
        lastName: str | None = None,
        phone: str | None = None,
        companyName: str | None = None,
        tags: list[GoHighLevel] | None = None,
        customFields: list[CustomFieldSchema] | None = None
        ):       
        payload = ContactUpdate(
            firstName=firstName,
            lastName=lastName,
            phone=phone,
            companyName=companyName,
            tags=tags,
            customFields=customFields
            ).model_dump(exclude_none=True)
        data = await self.send_request("PUT", f"/contacts/{contact_id}", payload, self.headers)
        self.log(f"Contact updated: {data}")

    async def delete_contact(self, contact_id: str):
        data = await self.send_request("DELETE", f"/contacts/{contact_id}", headers=self.headers)
        self.log(f"Contact deleted: {data}")
        