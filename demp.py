from typing import Literal, List
from pydantic import BaseModel, Field
import bs4
import os

from langchain import hub
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.graph import StateGraph, START
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.chat_models import init_chat_model

# -------------------------------------------------------------------
# CONFIG
# -------------------------------------------------------------------
if not os.environ.get("GOOGLE_API_KEY"):
    os.environ["GOOGLE_API_KEY"] = "AIzaSyD0D5lO9oajtO-THvXKpMQy902QL8zGgFU"

# Initialize model + embeddings
llm = init_chat_model("gemini-2.5-flash", model_provider="google_genai")
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

# -------------------------------------------------------------------
# LOAD DOCUMENTS
# -------------------------------------------------------------------
loader = WebBaseLoader(
    web_paths=("https://lilianweng.github.io/posts/2023-06-23-agent/",),
    bs_kwargs=dict(
        parse_only=bs4.SoupStrainer(
            class_=("post-content", "post-title", "post-header")
        )
    ),
)
docs = loader.load()

# Split text into chunks
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
all_splits = splitter.split_documents(docs)

# Label sections
total = len(all_splits)
for i, doc in enumerate(all_splits):
    if i < total / 3:
        doc.metadata["section"] = "beginning"
    elif i < 2 * total / 3:
        doc.metadata["section"] = "middle"
    else:
        doc.metadata["section"] = "end"

# -------------------------------------------------------------------
# VECTOR STORE
# -------------------------------------------------------------------
vector_store = InMemoryVectorStore(embeddings)
_ = vector_store.add_documents(all_splits)

# -------------------------------------------------------------------
# STRUCTURED OUTPUT MODEL
# -------------------------------------------------------------------
class Search(BaseModel):
    query: str = Field(..., description="Search query to run.")
    section: Literal["beginning", "middle", "end", "all"] = Field(
        ..., description="Section to query. Can be 'beginning', 'middle', 'end', or 'all'."
    )

# -------------------------------------------------------------------
# STATE
# -------------------------------------------------------------------
class State(BaseModel):
    question: str
    query: Search | None = None
    context: List[Document] | None = None
    answer: str | None = None

# -------------------------------------------------------------------
# PROMPT
# -------------------------------------------------------------------
prompt = hub.pull("rlm/rag-prompt")

# -------------------------------------------------------------------
# GRAPH FUNCTIONS
# -------------------------------------------------------------------
def analyze_query(state: State):
    structured_llm = llm.with_structured_output(Search)
    query = structured_llm.invoke(state.question)
    return {"query": query}

def retrieve(state: State):
    query = state.query
    docs = vector_store.similarity_search(
        query.query,
        filter=lambda d: d.metadata.get("section") == query.section,
    )
    return {"context": docs}

def generate(state: State):
    docs_content = "\n\n".join(d.page_content for d in state.context)
    messages = prompt.invoke({"question": state.question, "context": docs_content})
    result = llm.invoke(messages)
    return {"answer": result.content}

# -------------------------------------------------------------------
# BUILD GRAPH
# -------------------------------------------------------------------
graph = (
    StateGraph(State)
    .add_node("analyze_query", analyze_query)
    .add_node("retrieve", retrieve)
    .add_node("generate", generate)
    .add_edge(START, "analyze_query")
    .add_edge("analyze_query", "retrieve")
    .add_edge("retrieve", "generate")
    .compile()
)

# -------------------------------------------------------------------
# RUN
# -------------------------------------------------------------------
for step in graph.stream(
    {"question": "What does the end of the post say about Task Decomposition?"},
    stream_mode="updates",
):
    print(step)
    print("\n----------------\n")
