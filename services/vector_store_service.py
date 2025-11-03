from decouple import config
import os
from langchain_chroma import Chroma
from services.llm_service import LLMService
import os

# Class: VectorStoreService
# -------------------------
# Manages vector database connections and embedding initialization
# using Google Generative AI embeddings and Chroma for persistence.


class VectorStoreService:
    def __init__(self):
        os.makedirs(str(config("VECTOR_DB_DIR")), exist_ok=True)
        self.__embedding = LLMService().get_embedding_model()

    def vector_db(self):
        return Chroma(
            collection_name="video_summaries",
            embedding_function=self.__embedding,
            persist_directory=str(config("VECTOR_DB_DIR")),
        )

    def llm(self):
        return LLMService().get_chat_model()
