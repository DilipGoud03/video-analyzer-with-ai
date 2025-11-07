from langgraph.checkpoint.memory import MemorySaver
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, START, END
from decouple import config
import os
import mimetypes
import base64
import sys
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain_text_splitters import RecursiveCharacterTextSplitter
from services.vector_store import VectorStoreService
from services.llm import LLMService
from uuid import uuid4
from langchain_mcp_adapters.client import MultiServerMCPClient
import traceback
import asyncio
from langchain_core.tools import StructuredTool

# ------------------------------------------------------------
# TypedDict: UploadedFile
# Description:
#   Represents an uploaded video file, including its MIME type
#   and raw binary data for model input.
# ------------------------------------------------------------


class UploadedFile(TypedDict):
    mime_type: str
    data: bytes


# ------------------------------------------------------------
# TypedDict: MainState
# Description:
#   Defines the shared state for the LangGraph workflow.
#   Stores input video, model-generated summary, and
#   question-answer pairs for the interactive session.
# ------------------------------------------------------------
class MainState(TypedDict):
    video_path: Optional[str]
    video_name: str
    uploaded_file: Optional[UploadedFile]
    summary: Optional[str]
    is_new_video: bool
    prompt: Optional[str]
    question: Optional[str]
    answer: Optional[str]


# ------------------------------------------------------------
# Class: LanggraphService
# Description:
#   Encapsulates all LangGraph workflow nodes for video
#   summarization and question-answering. Each method serves as
#   an independent node connected within a StateGraph pipeline.
# ------------------------------------------------------------
class LanggraphService:
    def __init__(self):
        # ------------------------------------------------------------
        # Global Initializations
        # ------------------------------------------------------------
        # Initializes the vector store service and chat model for use
        # throughout the LangGraph workflow. This allows persistence
        # of summaries and intelligent responses using embeddings.
        # ------------------------------------------------------------
        self.__vector_service = VectorStoreService()
        self.__llm = LLMService().get_chat_model()
        self.__llm_with_tools = None
        self.__mcp_client = None

    # ------------------------------------------------------------
    # Async: initialize_mcp
    # Description:
    #   Starts the MCP stdio server (VideoDatabase) and loads
    #   all available tools for the LLM to use.
    # ------------------------------------------------------------
    async def initialize_mcp(self):
        print("Starting MCP initialization...")
        try:
            server_path = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "mcp/server.py")
            )

            self.__mcp_client = MultiServerMCPClient({
                "VideoDatabase": {
                    "transport": "stdio",
                    "command": sys.executable,
                    "args": [server_path],
                }
            })

            # Fetch raw MCP tools
            raw_tools = await self.__mcp_client.get_tools()

            # Convert each MCP tool → LangChain StructuredTool
            wrapped_tools = []
            for tool in raw_tools:
                async def _call_tool(**kwargs):
                    return await self.__mcp_client.call_tool(tool.name, kwargs)

                wrapped_tool = StructuredTool.from_function(
                    func=_call_tool,
                    name=tool.name,
                    description=tool.description or "MCP tool",
                )
                wrapped_tools.append(wrapped_tool)

            self.__llm_with_tools = self.__llm.bind_tools(wrapped_tools)

            print("LLM successfully bound with MCP tools.")
            return wrapped_tools

        except Exception as e:
            print(f"MCP initialization failed: {e}")
            traceback.print_exc()
            self.__mcp_tools = []
            self.__llm_with_tools = self.__llm
            return []

    # ------------------------------------------------------------
    # Node: upload_video
    # Description:
    #   Loads and processes the uploaded video file into memory for downstream nodes.
    # ------------------------------------------------------------

    def upload_video(self, state: MainState):
        path = state.get("video_path")
        if not path or not os.path.exists(path):
            raise FileNotFoundError("Video path not provided or invalid")

        mime_type, _ = mimetypes.guess_type(path)
        mime_type = mime_type or "video/mp4"

        with open(path, "rb") as f:
            video_bytes = f.read()

        return {"uploaded_file": {"mime_type": mime_type, "data": video_bytes}}

    # ------------------------------------------------------------
    # Node: summarize_video
    # Description:
    #   Sends the uploaded video to the Gemini model for analysis
    #   and generates a natural, human-readable summary describing
    #   scenes, actions, and emotions without introductory phrases.
    # ------------------------------------------------------------

    def summarize_video(self, state: MainState):
        uploaded_file = state["uploaded_file"]
        prompt = """
            Provide a detailed and comprehensive description of this video. 
            Your response must be in a natural human-readable format describing 
            what happens in the video, including scenes, actions, objects, and emotions. 
            Do not include any meta phrases like 'Here is the summary' — start directly.
        """

        if 'prompt' in state and state['prompt'] != '':
            prompt = f"{state['prompt']} Avoid adding introductory phrases like 'Here is the summary' or 'Okay, here’s the explanation'. Start directly with the summary content."

        encoded_video = base64.b64encode(uploaded_file["data"]).decode("utf-8")
        message = HumanMessage(
            content=[
                {"type": "text", "text": prompt},
                {"type": "media", "data": encoded_video,
                    "mime_type": uploaded_file["mime_type"]},
            ]
        )

        response = self.__llm.invoke([message])
        return {"summary": response.content}
    
    # ------------------------------------------------------------
    # async Node: validate_and_update_video
    # Description:
    #   Sends the summary of provided video to MCP Tool
    #   MCP tool analyze the summary and retrive the category and suitaibilty based on summary content
    #   and update this details by using mcp server in database.
    # ------------------------------------------------------------

    async def validate_and_update_video(self, state: MainState):
        if state.get("is_new_video") and state["is_new_video"] is True:
            summary = state.get("summary", "No summary available")
            prompt = f"""
                Analyze the video summary: '{summary}'.
                Determine category (Like in Film & Animation, Autos & Vehicles, Pets & Animals, Travel & Events, People & Blogs, News & Politics, Science & Technology, Howto & Style, Nonprofits & Activism, Music, Sports, Short, Movies Education, Gaming, Videoblogging, Comedy, Entertainment, Movies, Anime/Animation, Action/Adventure, Sci-Fi/Fantasy, Classics, Comedy, Documentary, Drama, Family, Foreign, Horror, Thriller, Shorts, Shows, Trailers) 
                and suitability (use ONLY: 'under_5, 'under_10','under_13','under_16','under_18','adult').
                Call update_video_metadata with video_name='{state['video_name']}', category, suitability.
            """

            response = await self.__llm_with_tools.ainvoke([HumanMessage(content=prompt)])
            if hasattr(response, "tool_calls") and response.tool_calls:
                for call in response.tool_calls:
                    async with self.__mcp_client.session("VideoDatabase") as session:
                        data = await session.call_tool(call["name"], arguments=call["args"]["kwargs"])
                        print("data", data)
        return {}

    # ------------------------------------------------------------
    # Node: store_summary_in_db
    # Description:
    #   Persists the generated video summary into the Chroma vector
    #   database for future semantic retrieval and question-answering.
    #   Skips storage if not marked as a new video.
    # ------------------------------------------------------------
    def store_summary_in_db(self, state: MainState):
        vector_db = self.__vector_service.vector_db()
        if state.get("is_new_video") and state["is_new_video"] is True:
            try:
                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=200,
                    chunk_overlap=50,
                    length_function=len,  # Measure by characters
                    separators=["\n\n", "\n", " ", ""]
                )
                # Create chunks with metadata
                chunks = text_splitter.split_text(state["summary"])
                documents = []
                if chunks and len(chunks) > 0:
                    for chunk in chunks:
                        documents.append(
                            Document(
                                page_content=chunk,
                                metadata={"source": state["video_name"]}
                            )
                        )
                if len(documents) > 0:
                    uuids = [str(uuid4()) for _ in range(len(documents))]
                    vector_db.add_documents(documents=documents, ids=uuids)
                return {}
            except Exception as e:
                print(f"Error saving summary: {e}")
        return {}

    # ------------------------------------------------------------
    # Node: ask_question
    # Description:
    #   Retrieves stored summaries from the vector DB and uses a
    #   retrieval-augmented generation (RAG) chain to answer user
    #   questions based on the video content.
    # ------------------------------------------------------------

    def ask_question(self, state: MainState):
        question = state.get("question")
        video_name = state.get("video_name")

        vector_db = self.__vector_service.vector_db()

        filter_query = {"source": video_name}
        retriever = vector_db.as_retriever(
            search_kwargs={'filter': filter_query})

        rag_prompt = ChatPromptTemplate.from_messages([
            ("system",
             "You are an intelligent AI assistant. Use the following video context to answer the question directly and clearly. "
             "Do not say things like 'Based on the provided video text' or 'According to the context' also always use video instead of context and text.\n\n"
             "Context:\n{context}"),
            ("human", "{input}")
        ])

        combine_docs_chain = create_stuff_documents_chain(
            self.__llm, rag_prompt)
        retrieval_chain = create_retrieval_chain(retriever, combine_docs_chain)

        result = retrieval_chain.invoke({"input": question})
        return {"answer": result["answer"]}

    # ------------------------------------------------------------
    # Node: conditional_node
    # Description:
    #   Determines which node in the workflow to start from based
    #   on the user's input type — a question or a new video upload.
    # ------------------------------------------------------------

    def conditional_node(self, state: MainState) -> str:
        if state.get("question") and state['question'] != '':
            return "ask_question"
        return "upload_video"

    def build_pipeline(self, is_questioning: bool = False):
        pipeline = StateGraph(MainState)

        # Add nodes
        pipeline.add_node("upload_video", self.upload_video)
        pipeline.add_node("validate_and_update_video", lambda state: asyncio.run(
            self.validate_and_update_video(state)))
        pipeline.add_node("summarize_video", self.summarize_video)
        pipeline.add_node("store_summary_in_db", self.store_summary_in_db)
        pipeline.add_node("ask_question", self.ask_question)

        # Conditional edges
        pipeline.add_conditional_edges(
            START,
            self.conditional_node,
            {
                "upload_video": "upload_video",
                "ask_question": "ask_question",
            },
        )

        # Sequential edges
        pipeline.add_edge("upload_video", "summarize_video")
        pipeline.add_edge("summarize_video", "validate_and_update_video")
        pipeline.add_edge("summarize_video", "store_summary_in_db")
        pipeline.add_edge("store_summary_in_db", END)
        pipeline.add_edge("ask_question", END)

        # Compile with or without memory saver
        if is_questioning:
            checkpointer = MemorySaver()
            return pipeline.compile(checkpointer=checkpointer)
        return pipeline.compile()
