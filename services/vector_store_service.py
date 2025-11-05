from decouple import config
import os
from langchain_chroma import Chroma
from services.llm_service import LLMService

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
    #   and sets up the embedding and LLM instances via LLMService.
    # ------------------------------------------------------------
    def __init__(self):
        os.makedirs(str(config("VECTOR_DB_DIR")), exist_ok=True)
        self.__embedding = LLMService().get_embedding_model()
        self.__llm = LLMService().get_chat_model()

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
        return Chroma(
            collection_name="video_summaries",
            embedding_function=self.__embedding,
            persist_directory=str(config("VECTOR_DB_DIR")),
        )

    # ------------------------------------------------------------
    # Method: _delete_documents
    # Description:
    #   Removes document embeddings from both Chroma stores.
    # ------------------------------------------------------------
    def _delete_documents(self, file_name):
        vector_store = self.vector_db()
        # Delete all documents for a specific video
        try:
            vector_store.delete(where={"video_name": file_name})
        except Exception as e:
            print(f"No documents found or error deleting: {e}")
            # Continue without error

        return True

    # ------------------------------------------------------------
    # Method: get_documents
    # Description:
    #   Get All document embeddings from both Chroma stores.
    # ------------------------------------------------------------
    def get_documents(self):
        vector_store = self.vector_db()
        return True