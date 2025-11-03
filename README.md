# 🎥 Video Analyzer with AI

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-App-red?logo=streamlit)
![LangChain](https://img.shields.io/badge/LangChain-Framework-green?logo=chainlink)
![LangGraph](https://img.shields.io/badge/LangGraph-Orchestration-orange?logo=graph)
![ChromaDB](https://img.shields.io/badge/ChromaDB-VectorStore-purple?logo=databricks)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

**Video Analyzer with AI** is an advanced AI-powered tool built using **LangChain**, **LangGraph**, and **ChromaDB**.  
It analyzes videos, generates summaries, stores them in a vector database, and enables interactive **question-answering** about the video content.  

All of this is wrapped inside a **Streamlit** UI for a seamless user experience.

---

## 🚀 Key Features

- 🧠 **LangChain + LangGraph Pipeline** – Graph-based orchestration of video analysis stages.  
- 🎬 **Automatic Summarization** – Extract concise summaries from video transcripts.  
- 💬 **Q&A over Stored Context** – Ask questions about previously processed videos using **ChromaDB** for retrieval.  
- 💾 **Persistent Memory** – Video summaries are embedded and stored for future re-querying.  
- 🔍 **Optional Web Search** – Augment answers with external data (via SerperDev WebSearch).  
- ⚡ **Streamlit Frontend** – Simple and modern web interface.  
- 🔐 **Environment-Based Config** – Plug in your OpenAI, Gemini, and Serper keys easily.  

---

## 🛠️ Technologies Used
|-----------|------------------|
| **Language** | Python 3.10+ |
| **Framework** | Streamlit |
| **AI / NLP** | LangChain, LangGraph, OpenAI, Google Gemini |
| **Search & Context** | Haystack, SerperDev WebSearch |
| **Embeddings** | Google Generative AI, OpenAI Embeddings |
| **Utilities** | Pandas, dotenv, OS |
| **Environment** | `.env` for configuration |

---

## LangChain + LangGraph Integration

LangChain provides the core building blocks for LLM interactions (prompts, chains, and tools).  
**LangGraph** orchestrates these blocks into a **graph-based workflow**, making multi-step reasoning and tool execution seamless.

### Example Flow
Video Input
    ↓
    Transcription Node
    ↓
    Summarization Node (LangChain)
    ↓
    Q&A Node (LangGraph Conditional Edge)
    ↓
    Result → Display on Streamlit


## 🛠️ Tech Stack

| Category | Tools / Libraries |
|-----------|------------------|
| **Language** | Python 3.10+ |
| **Frontend** | Streamlit |
| **AI / LLMs** | LangChain, LangGraph, OpenAI, Google Gemini |
| **Vector Database** | ChromaDB |
| **Web Search (optional)** | Haystack, SerperDev WebSearch |
| **Embeddings** | GoogleGenerativeAIEmbeddings, OpenAIEmbeddings |
| **Environment** | Python-dotenv, OS, Pandas |

## ⚡ Installation

1. **Clone this repo**

   ```bash
   git clone https://github.com/DilipGoud03/video-analyzer-with-ai.git
    cd video-analyzer-with-ai
   ```
   
2. **Create and Activate virtual Enviorment**

   1. Create a virtual environment.

      ```bash
      python -m venv video-analyzer-venv
      ```

   2. Activate virtual environment.

      ```bash
      source video-analyzer-venv/bin/activate
      ```
2. **Install dependencies**

      ```bash
      pip install -r requirements.txt
      ```

3. **Configure environment**
   - Copy `.env-copy` to `.env`
   - Fill in your DB credentials, API key etc.

4. **Start the server**
   ```bash
   streamlit run streamlit_app.py

   ```

##  How to Use
The project uses **LangGraph** to control the workflow and **LangChain** tools for LLM reasoning and embeddings.  
Summaries are stored in **ChromaDB** to enable retrieval-augmented generation (RAG) for video Q&A.