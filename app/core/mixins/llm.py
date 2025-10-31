from langchain_openai import ChatOpenAI
from app.core.config.config import settings

class LLMMixin:
    def get_llm(self, schema):
        llm = ChatOpenAI(
            model=settings.open_ai.CHAT_MODEL,
            api_key=settings.open_ai.OPENAI_API_KEY
        )
        return llm.with_structured_output(schema)
