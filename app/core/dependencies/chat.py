from typing import Annotated

from fastapi import Depends

from app.services.chat_bot_service import ChatLangchainService
from app.core.dependencies import KnowledgeBaseServiceDep


async def get_chat_bot_service(knowledge_base_service: KnowledgeBaseServiceDep) -> ChatLangchainService:
    return ChatLangchainService(kb=knowledge_base_service)

ChatBotServiceDep = Annotated[ChatLangchainService, Depends(get_chat_bot_service)]
