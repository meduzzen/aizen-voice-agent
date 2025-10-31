import os, json
import tempfile
from pathlib import Path
from typing import Any, Optional, List

from fastapi import UploadFile
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    UnstructuredWordDocumentLoader,
)
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core import settings


class KnowledgeBaseService:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(
            model=settings.vector_bd.EMBEDDING_MODEL,
            api_key=settings.open_ai.OPENAI_API_KEY,
        )
        self.persist_directory = settings.vector_bd.PERSIST_DIRECTORY
        self.default_collection = settings.vector_bd.COLLECTION_NAME
        self.db: Optional[Chroma] = None

        base_tmp = getattr(getattr(settings, "app", object()), "TMP_DIR", None)
        self.tmp_dir = Path(base_tmp) if base_tmp else Path(tempfile.gettempdir()) / "aizen_kb"
        self.tmp_dir.mkdir(parents=True, exist_ok=True)

    def get_db(self, collection_name: str) -> Chroma:
        return Chroma(
            collection_name=collection_name,
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings,
        )

    def get_retriever(self, collection_name: str, k: int = 3):
        return self.get_db(collection_name).as_retriever(search_kwargs={"k": k})

    @property
    def loader(self) -> dict[str, Any]:
        return {
            "pdf": PyPDFLoader,
            "txt": TextLoader,
            "doc": UnstructuredWordDocumentLoader,
            "docx": UnstructuredWordDocumentLoader,
            "json": None,
        }

    async def _save_upload_to_temp(self, file: UploadFile, ext: str) -> Path:
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}", dir=self.tmp_dir) as tmp:
            while True:
                chunk = await file.read(1024 * 1024)
                if not chunk:
                    break
                tmp.write(chunk)
            tmp_path = Path(tmp.name)
        await file.seek(0)
        return tmp_path

    async def file_preprocessing(self, file: UploadFile, flow: Optional[str] = None) -> List[Document]:
        ext = file.filename.split(".")[-1].lower()
        temp_path: Optional[Path] = None

        try:
            if ext == "json":
                temp_path = await self._save_upload_to_temp(file, ext)
                data = json.loads(temp_path.read_text(encoding="utf-8"))
                docs: List[Document] = []
                flow_val = flow or "general"
                for sec_idx, sec in enumerate(data):
                    section = sec.get("section", "General")
                    if "qa_groups" in sec:
                        for g_idx, g in enumerate(sec["qa_groups"]):
                            q_hints = g.get("q_hints", [])
                            for a_idx, ans in enumerate(g.get("answers", [])):
                                content = ans + "\n\n" + "\n".join(q_hints)
                                docs.append(Document(
                                    page_content=content,
                                    metadata={
                                        "flow": flow_val,
                                        "section": section,
                                        "sec_idx": sec_idx, "g_idx": g_idx, "a_idx": a_idx,
                                        "source": file.filename
                                    }
                                ))
                    else:
                        q_hints = sec.get("user_questions", [])
                        for a_idx, ans in enumerate(sec.get("answers", [])):
                            content = ans + "\n\n" + "\n".join(q_hints)
                            docs.append(Document(
                                page_content=content,
                                metadata={
                                    "flow": flow_val,
                                    "section": section,
                                    "sec_idx": sec_idx, "g_idx": 0, "a_idx": a_idx,
                                    "source": file.filename
                                }
                            ))
                return docs

            if ext not in self.loader:
                raise ValueError(f"Unsupported file format: {ext}")

            temp_path = await self._save_upload_to_temp(file, ext)
            loader_class = self.loader[ext]
            loader = loader_class(str(temp_path))

            if hasattr(loader, "aload"):
                documents = await loader.aload()
            else:
                from anyio.to_thread import run_sync
                documents = await run_sync(loader.load)
            return documents

        finally:
            if temp_path and temp_path.exists():
                try:
                    temp_path.unlink()
                except Exception:
                    pass

    @staticmethod
    async def split_document(documents: list[Document]) -> list[Document]:
        splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(chunk_size=500, chunk_overlap=50)
        return splitter.split_documents(documents)

    async def save_to_chroma(self, docs: List[Document], collection_name: str) -> None:
        db = self.get_db(collection_name)
        await db.aadd_documents(docs)

    async def retrieve(self, query: str, collection_name: str, k: int = 3) -> str:
        db = self.get_db(collection_name)
        results = await db.asimilarity_search_with_relevance_scores(query=query, k=k)

        return "\n\n - -\n\n".join([doc.page_content for doc, _score in results])

    async def load_to_memory(self, file: UploadFile, collection_name: str, flow: Optional[str] = None):
        documents = await self.file_preprocessing(file, flow=flow)
        if file.filename.lower().endswith(".json"):
            split_documents = documents
        else:
            split_documents = await self.split_document(documents)
        await self.save_to_chroma(split_documents, collection_name=collection_name)
