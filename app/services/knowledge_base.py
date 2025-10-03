import os
from typing import Any

from fastapi import UploadFile
from langchain.schema.document import Document
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
        self.collection_name = settings.vector_bd.COLLECTION_NAME
        self.db = self.get_db()

    def get_db(self) -> None | Chroma:
        return Chroma(
            collection_name=self.collection_name,
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings,
        )

    @property
    def loader(self) -> dict[str, Any]:
        return {
            "pdf": PyPDFLoader,
            "txt": TextLoader,
            "doc": UnstructuredWordDocumentLoader,
            "docx": UnstructuredWordDocumentLoader,
        }

    async def file_preprocessing(self, file: UploadFile) -> list[Document]:
        ext = file.filename.split(".")[-1].lower()
        if ext not in self.loader:
            raise ValueError(f"Unsupported file format: {ext}")

        temp_path = f"/tmp/{file.filename}"
        with open(temp_path, "wb") as f:
            f.write(await file.read())

        loader_class = self.loader[ext]
        loader = loader_class(temp_path)
        documents = await loader.aload()
        os.remove(temp_path)
        return documents

    @staticmethod
    async def split_document(documents: list[Document]) -> list[Document]:
        splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(chunk_size=500, chunk_overlap=50)
        return splitter.split_documents(documents)

    async def save_to_chroma(self, docs: list[Document]) -> None:
        if self.db:
            await self.db.aadd_documents(docs)
        else:
            self.db = await Chroma.afrom_documents(
                documents=docs,
                embedding=self.embeddings,
                persist_directory=self.persist_directory,
                collection_name=self.collection_name,
            )

    async def retrieve(self, query: str, k: int = 3) -> str:
        if not self.db:
            self.db = self.get_db()
        results = await self.db.asimilarity_search_with_relevance_scores(query=query, k=k)

        return "\n\n - -\n\n".join([doc.page_content for doc, _score in results])

    async def load_to_memory(self, file: UploadFile):
        documents = await self.file_preprocessing(file)
        split_documents = await self.split_document(documents)
        await self.save_to_chroma(split_documents)
