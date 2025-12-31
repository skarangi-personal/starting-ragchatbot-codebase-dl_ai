# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Course Materials RAG System** - A full-stack Retrieval-Augmented Generation application that allows users to query course materials semantically and receive AI-powered responses. Uses ChromaDB for vector search, Anthropic Claude for response generation, and FastAPI for the backend API.

**Tech Stack**: Python 3.13, FastAPI, ChromaDB, Anthropic Claude API, Vanilla JavaScript frontend

## Architecture

### Core Components

The system follows a layered architecture with clear separation of concerns:

```
Frontend (HTML/CSS/JS)
    ↓ HTTP
FastAPI App (app.py)
    ↓
RAGSystem (rag_system.py) - Central Orchestrator
    ├─ DocumentProcessor (document_processor.py)
    │   └─ Parses course files, extracts metadata, chunks text
    ├─ VectorStore (vector_store.py)
    │   └─ ChromaDB wrapper for semantic search
    ├─ AIGenerator (ai_generator.py)
    │   └─ Anthropic Claude integration with tool support
    ├─ SessionManager (session_manager.py)
    │   └─ Manages conversation history per session
    └─ ToolManager + SearchTools (search_tools.py)
        └─ Implements function calling for course-specific searches
```

### Key Design Patterns

1. **RAGSystem as Orchestrator**: `RAGSystem` coordinates all components and manages the query-response flow. All backend logic flows through this class.

2. **Tool-Based Search**: Uses Anthropic's function calling feature (`search_tools.py`) to allow Claude to dynamically search course content. The `CourseSearchTool` class defines the schema for searches.

3. **Session Management**: Maintains conversation context using session IDs. Sessions are keyed by session ID and stored in-memory with configurable history length.

4. **Chunked Storage**: Course documents are split into overlapping chunks (800 char chunks with 100 char overlap by default) for better semantic search in ChromaDB.

5. **Pydantic Models**: Data validation for all API request/response contracts. Core domain models: `Course`, `Lesson`, `CourseChunk`.

### Data Flow for a Query

1. Frontend sends POST `/api/query` with query text and optional session_id
2. FastAPI validates request with `QueryRequest` Pydantic model
3. RAGSystem orchestrates:
   - Session loading (or creation)
   - Vector search via `CourseSearchTool` (tool calling)
   - Claude API call with search results + conversation history
   - Response formatting with sources
4. Response returned as `QueryResponse` (answer, sources, session_id)
5. Frontend parses JSON and renders with Marked.js

## Common Development Tasks

### Running the Application

**Always use `uv` to run the server - never use `pip`.**

```bash
# Quick start with shell script
chmod +x run.sh
./run.sh

# Or manually (from project root)
cd backend
uv run uvicorn app:app --reload --port 8000
```

Access the app at `http://localhost:8000` and API docs at `http://localhost:8000/docs`

### Adding a New Course Document

```python
# In backend code
from rag_system import RAGSystem
from config import config

rag = RAGSystem(config)
course, chunks = rag.add_course_document("path/to/course.txt")
```

Documents are automatically loaded from `../docs` folder on startup if they exist.

### Modifying Search Behavior

Edit `config.py`:
- `CHUNK_SIZE`: Text chunk size for vector storage (default 800)
- `CHUNK_OVERLAP`: Overlap between chunks (default 100)
- `MAX_RESULTS`: Max search results returned (default 5)
- `MAX_HISTORY`: Conversation messages to retain (default 2)

### Adding a New API Endpoint

1. Add Pydantic model for request/response in `models.py` (or `app.py` if simple)
2. Add async function to `app.py` decorated with `@app.post()` or `@app.get()`
3. Call appropriate `RAGSystem` or component methods
4. Use `HTTPException` for error handling

Example:
```python
@app.post("/api/new-endpoint", response_model=ResponseModel)
async def new_endpoint(request: RequestModel):
    try:
        result = rag_system.some_method(request.param)
        return ResponseModel(data=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Modifying AI Behavior

Edit `ai_generator.py`:
- `SYSTEM_PROMPT`: Adjust Claude's instructions
- Model version: Change `claude-sonnet-4-20250514` in `config.py`
- Tool definitions: Modify `search_tools.py` to add/change function calling schema

### Debugging

- FastAPI auto-generates OpenAPI docs at `/docs` - useful for testing endpoints
- `print()` statements in Python log to console during development (reload mode active)
- Frontend errors visible in browser console (F12)
- ChromaDB stores embeddings in `./chroma_db` directory - delete to reset

## Directory Structure

```
/backend
  app.py                  # FastAPI app, routes, startup logic
  config.py               # Configuration dataclass, environment loading
  rag_system.py           # Main orchestrator
  document_processor.py   # Document parsing, chunking, metadata extraction
  vector_store.py         # ChromaDB wrapper with add/search/clear operations
  ai_generator.py         # Anthropic Claude integration
  session_manager.py      # Session tracking and conversation history
  search_tools.py         # Function calling tool definitions
  models.py               # Pydantic models: Course, Lesson, CourseChunk

/frontend
  index.html              # Web page structure
  script.js               # Client-side logic, API calls, UI updates
  style.css               # Styling and layout

/docs                     # Course material .txt files (loaded on startup)

.env.example              # Environment variable template
run.sh                    # Shell script entry point
pyproject.toml            # UV project config, dependencies
uv.lock                   # Locked dependency versions
```

## Configuration

### Environment Setup

1. Create `.env` file in project root with:
   ```
   ANTHROPIC_API_KEY=your_api_key_here
   ```

2. Python 3.13 is required (specified in `.python-version`)

3. UV package manager required - install via:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

### Key Configuration in `config.py`

- `ANTHROPIC_MODEL`: Claude model version (currently `claude-sonnet-4-20250514`)
- `EMBEDDING_MODEL`: Sentence transformer for embeddings (`all-MiniLM-L6-v2`)
- `CHROMA_PATH`: Where ChromaDB stores vector data (`./ chroma_db`)

## Important Implementation Details

### Vector Search

- Uses ChromaDB with sentence-transformers embeddings
- CourseSearchTool searches both course metadata and chunk content
- Results limited by `MAX_RESULTS` config
- Search is called via Claude's function calling - Claude decides when/how to search

### Response Generation

Claude receives:
1. System prompt with instructions
2. Conversation history (limited by `MAX_HISTORY`)
3. User query
4. Available tools (CourseSearchTool)

Claude can call CourseSearchTool to search, then generates final response with sources

### Frontend-Backend Communication

- JSON request/response via fetch API
- Session IDs persist state across requests
- Loading UI shown during processing
- Markdown rendering via Marked.js library
- No frontend framework - vanilla JS with manual DOM updates

### Error Handling

- Backend: HTTPException with status codes and error messages
- Tool execution failures: Handled in `ai_generator.py`, passed back to Claude
- Frontend: Error messages shown in chat interface

## Dependency Management & Running Python

**Always use UV - never use pip.**

UV is used for:
- **Dependency management**: `uv sync`, `uv add package_name`, `uv remove package_name`
- **Running Python files**: `uv run python script.py` or `uv run uvicorn app:app`
- **Running any command**: `uv run command` executes in the project's virtual environment

Key commands:
- `uv sync` - Install dependencies from lock file (run after pulling changes)
- `uv add package_name` - Add new dependency
- `uv remove package_name` - Remove a dependency
- `uv run python script.py` - Run any Python script
- `uv run uvicorn app:app --reload --port 8000` - Run the server
- Changes to dependencies propagate to `uv.lock` (commit this file)

Key dependencies:
- `fastapi==0.116.1` - Web framework
- `chromadb==1.0.15` - Vector database
- `anthropic==0.58.2` - Claude API client
- `sentence-transformers==5.0.0` - Embeddings
- `uvicorn==0.35.0` - ASGI server
- `python-dotenv==1.1.1` - Environment variables

## MCP Server Configuration

**Playwright MCP Server** - Only enable when browser automation is explicitly needed.

The Playwright MCP server is currently configured but should be **disabled by default** to conserve resources:

```bash
# Remove Playwright MCP server (default state)
claude mcp remove playwright -s local

# Only add when browser automation is needed
claude mcp add --transport stdio playwright -- npx -y @playwright/mcp@latest

# Verify status
claude mcp get playwright
```

**When to enable Playwright:**
- Web scraping or content extraction from external websites
- Automated browser interactions for testing
- Screenshot capture for documentation
- Form filling or web automation tasks

**Note**: MCP servers only execute when their tools are actively used, but keeping them disconnected when not needed is preferred for this project.

## Notes for Future Work

- No test suite currently exists
- Session data is in-memory (lost on restart) - consider persistent storage for production
- ChromaDB is local file-based - suitable for development, consider managed service for production
- Static file serving is development-focused (no-cache headers) - optimize for production
- CORS currently allows all origins (`*`) - restrict in production
- Document loading is automatic from `docs/` folder on startup
