from typing import AsyncIterator, Dict, Any, List
from pydantic import ValidationError

from fastapi import WebSocket, WebSocketDisconnect
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from app.schemas.chat_bot import MsgType, ClientMessage
from app.services.flow_classifier import classify_flow
from app.core.config.prompts import Prompts
from app.core import settings
from app.services.knowledge_base import KnowledgeBaseService


FLOW_TO_COLLECTION = {
    "candidate": settings.vector_bd.COLLECTION_CANDIDATES,
    "client": settings.vector_bd.COLLECTION_CLIENTS,
}


class ChatLangchainService:
    def __init__(self, kb: KnowledgeBaseService):
        self.kb = kb
        self.llm = ChatOpenAI(
            model=settings.open_ai.CHAT_MODEL,
            api_key=settings.open_ai.OPENAI_API_KEY,
            streaming=True,
            temperature=0.2,
        )
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", Prompts.CHAT_BOT_PROMPT),
            ("system", "CONTEXT:\n{context}"),
            ("user", "{question}"),
        ])
        self.parser = StrOutputParser()
        self.greeting = "Hi! How can I help you?"

    async def _gather_context(self, question: str) -> str:
        decision = classify_flow(question)
        flows = decision.flows  # ["candidate"], ["client"], or ["candidate","client"]
        chunks: List[str] = []

        for fl in flows:
            col = FLOW_TO_COLLECTION.get(fl)
            if not col:
                continue
            retriever = self.kb.get_retriever(col, k=3)
            docs = await retriever.ainvoke(question)
            if docs:
                chunks.extend([d.page_content for d in docs])

        # dedup + limit
        uniq = []
        seen = set()
        for c in chunks:
            key = c.strip()[:200]
            if key not in seen:
                seen.add(key)
                uniq.append(c)
        return "\n\n---\n\n".join(uniq[:6])

    async def stream_answer(self, question: str) -> AsyncIterator[Dict[str, Any]]:
        context = await self._gather_context(question)
        chain = (
            {"question": RunnablePassthrough(), "context": lambda _: context}
            | self.prompt
            | self.llm
            | self.parser
        )
        async for chunk in chain.astream(question):
            yield {"type": "delta", "text": chunk}
        yield {"type": "end"}

    async def _send_greeting(self, ws: WebSocket) -> None:
        await ws.send_json({"type": MsgType.START.value})
        await ws.send_json({"type": MsgType.DELTA.value, "text": self.greeting})
        await ws.send_json({"type": MsgType.END.value})

    async def handle_ws(self, ws: WebSocket) -> None:
        await ws.accept()
        await self._send_greeting(ws)
        try:
            while True:
                raw = await ws.receive_json()
                try:
                    msg = ClientMessage.model_validate(raw)
                except ValidationError:
                    await ws.send_json({"type": MsgType.ERROR.value, "text": "Invalid payload"})
                    continue

                q = msg.text
                await ws.send_json({"type": MsgType.START.value})
                async for event in self.stream_answer(q):
                    await ws.send_json(event)

        except WebSocketDisconnect:
            return
        except Exception as e:
            await ws.send_json({"type": MsgType.ERROR.value, "text": str(e)})
