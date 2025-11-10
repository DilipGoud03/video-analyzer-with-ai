from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from decouple import config
from logger_app import setup_logger
# ------------------------------------------------------------
# Class: LLMService
# Description:
#   Handles initialization of LLMs (chat & embedding) based on
#   the selected provider ("openai" or "google").
#   This class provides abstraction to easily switch between
#   Gemini (Google) and GPT (OpenAI) models.
# ------------------------------------------------------------


class LLMService:
    # ------------------------------------------------------------
    # Method: __init__
    # Description:
    #   Initializes the configuration values from env.
    # ------------------------------------------------------------
    def __init__(self):
        self.__provider = str(config("PROVIDER"))
        self.__chat_model = str(config("CHAT_MODEL"))
        self.__embedding_model = str(config("EMBEDDING_MODEL"))
        self.__logger = setup_logger(__name__
                                     )

    # ------------------------------------------------------------
    # Method: gemini_chat_model
    # Description:
    #   Returns the Google Gemini chat model instance using
    #   the latest "gemini-2.5-flash" version.
    # ------------------------------------------------------------

    def gemini_chat_model(self):
        self.__logger.info("===setup_logger===")
        return ChatGoogleGenerativeAI(
            model=self.__chat_model,
            temperature=0,
            max_output_tokens=None,
            timeout=None,
            max_retries=2,
        )

    # ------------------------------------------------------------
    # Method: openai_chat_model
    # Description:
    #   Returns the OpenAI GPT chat model instance.
    #   Uses "gpt-4o-mini" for cost-effective responses.
    # ------------------------------------------------------------
    def gemini_embedding_model(self):
        self.__logger.info("===gemini_embedding_model===")
        return GoogleGenerativeAIEmbeddings(
            model=self.__embedding_model
        )

    # ------------------------------------------------------------
    # Method: openai_chat_model
    # Description:
    #   Returns the OpenAI GPT chat model instance.
    #   Uses "gpt-4o-mini" for cost-effective responses.
    # ------------------------------------------------------------
    def openai_chat_model(self):
        self.__logger.info("===openai_chat_model===")
        return ChatOpenAI(model=self.__chat_model, temperature=0, verbose=True)

    # ------------------------------------------------------------
    # Method: openai_embedding_model
    # Description:
    #   Returns the OpenAI embedding model used for text
    #   similarity, clustering, or semantic search.
    # ------------------------------------------------------------
    def openai_embedding_model(self):
        self.__logger.info("===openai_embedding_model===")
        return OpenAIEmbeddings(model=self.__embedding_model)

    # ------------------------------------------------------------
    # Method: get_chat_model
    # Description:
    #   Automatically returns the appropriate chat model
    #   depending on the configured provider.
    # ------------------------------------------------------------
    def get_chat_model(self):
        self.__logger.info("===get_chat_model===")

        if self.__provider == 'openai':
            return self.openai_chat_model()
        return self.gemini_chat_model()

    # ------------------------------------------------------------
    # Method: get_embedding_model
    # Description:
    #   Automatically returns the appropriate embedding model
    #   depending on the configured provider.
    # ------------------------------------------------------------
    def get_embedding_model(self):
        self.__logger.info("===get_embedding_model===")
        if self.__provider == 'openai':
            return self.openai_embedding_model()
        return self.gemini_embedding_model()
