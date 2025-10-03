from pydantic import Field

from app.core.config.base import BaseConfig


class VectorDBBaseConfig(BaseConfig):
    EMBEDDING_MODEL: str = Field(..., alias="EMBEDDING_MODEL")
    PERSIST_DIRECTORY: str = Field("vector_db_data", alias="PERSIST_DIRECTORY")
    COLLECTION_NAME: str = Field("", alias="COLLECTION_NAME")
