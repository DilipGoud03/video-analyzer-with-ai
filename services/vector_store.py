from decouple import config
import os
from langchain_chroma import Chroma
from services.llm import LLMService
from logger_app import setup_logger
# ------------------------------------------------------------
# Class: VectorStoreService
# Description:
#   Handles vector database setup and initialization using
#   Chroma for persistence. It leverages the embedding and
#   chat model instances from LLMService, allowing seamless
#   integration with both OpenAI and Google Gemini models.
# ------------------------------------------------------------


class VectorStoreService:
    # ------------------------------------------------------------
    # Method: __init__
    # Description:
    #   Initializes the vector database directory (if missing)
    #   and set up the embedding instances via LLMService.
    #   also setup the logger for traking and debug data
    # ------------------------------------------------------------
    def __init__(self):
        self.__embedding = LLMService().get_embedding_model()
        self.__logger = setup_logger(__name__)
    # ------------------------------------------------------------
    # Method: vector_db
    # Description:
    #   Returns a Chroma vector store instance configured with:
    #     - Persistent directory from env (VECTOR_DB_DIR)
    #     - Embedding model for text encoding
    #     - "video_summaries" as the collection name
    #   This provides a persistent storage layer for semantic
    #   search and similarity-based retrieval operations.
    # ------------------------------------------------------------

    def vector_db(self):
        self.__logger.info("===vector_db===")
        return Chroma(
            collection_name="video_summaries",
            embedding_function=self.__embedding,
            persist_directory="./database/vector_db/chroma_db",
        )

    # ------------------------------------------------------------
    # Method: _delete_documents
    # Description:
    #   Removes document embeddings from Chroma store.
    # ------------------------------------------------------------
    def _delete_documents(self, file_name):
        self.__logger.info("===_delete_documents===")
        vector_store = self.vector_db()
        # Delete all documents for a specific video
        try:
            self.__logger.info("===_delete_documents->try===")
            vector_store.delete(where={"source": file_name})
        except Exception as e:
            self.__logger.error(f"===_delete_documents->except=== {str(e)}")

        return True

    # ------------------------------------------------------------
    # Method: get_documents
    # Description:
    #   Get All document embeddings from Chroma store.
    # ------------------------------------------------------------
    def get_documents(self):
        vector_store = self.vector_db()
        self.__logger.info(f"===_delete_documents->except=== {vector_store.get()}")
        return True
