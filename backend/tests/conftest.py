"""Pytest configuration and shared fixtures for the RAG system tests."""

import pytest
import os
import tempfile
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add backend directory to path for imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
from models import Course, Lesson, CourseChunk


@pytest.fixture
def temp_chroma_db():
    """Create a temporary ChromaDB directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def test_config(temp_chroma_db):
    """Create a test configuration with mocked paths and API key."""
    from config import Config

    test_cfg = Config()
    test_cfg.CHROMA_PATH = temp_chroma_db
    test_cfg.ANTHROPIC_API_KEY = "test-api-key"
    test_cfg.CHUNK_SIZE = 800
    test_cfg.CHUNK_OVERLAP = 100
    test_cfg.MAX_RESULTS = 5
    test_cfg.MAX_HISTORY = 2

    return test_cfg


@pytest.fixture
def mock_rag_system(test_config):
    """Create a mock RAG system for testing."""
    with patch("rag_system.RAGSystem") as mock_rag:
        instance = mock_rag.return_value

        # Mock key methods
        instance.session_manager = MagicMock()
        instance.session_manager.create_session.return_value = "session-123"
        instance.session_manager.get_conversation_history.return_value = []
        instance.session_manager.add_exchange = MagicMock()

        instance.query.return_value = (
            "Test answer based on course materials",
            [
                {"title": "Course 1", "url": None},
                {"title": "Course 2", "url": "https://example.com/course2"}
            ]
        )

        instance.get_course_analytics.return_value = {
            "total_courses": 2,
            "course_titles": ["Introduction to AI", "Advanced Machine Learning"]
        }

        instance.add_course_folder.return_value = (1, 10)
        instance.add_course_document.return_value = (
            Course(title="Test Course", lessons=[]),
            5
        )

        yield instance


@pytest.fixture
def test_client(mock_rag_system):
    """Create a FastAPI test client without static file mounting."""
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    from typing import List, Optional, Dict

    # Create app without static files
    app = FastAPI(title="Course Materials RAG System (Test)")

    # Add middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )

    # Define models (duplicate for isolation)
    class QueryRequest(BaseModel):
        query: str
        session_id: Optional[str] = None

    class SourceLink(BaseModel):
        title: str
        url: Optional[str] = None

    class QueryResponse(BaseModel):
        answer: str
        sources: List[SourceLink]
        session_id: str

    class CourseStats(BaseModel):
        total_courses: int
        course_titles: List[str]

    # Add API endpoints
    @app.post("/api/query", response_model=QueryResponse)
    async def query_documents(request: QueryRequest):
        """Process a query and return response with sources"""
        try:
            session_id = request.session_id
            if not session_id:
                session_id = mock_rag_system.session_manager.create_session()

            answer, sources = mock_rag_system.query(request.query, session_id)

            return QueryResponse(
                answer=answer,
                sources=sources,
                session_id=session_id
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/courses", response_model=CourseStats)
    async def get_course_stats():
        """Get course analytics and statistics"""
        try:
            analytics = mock_rag_system.get_course_analytics()
            return CourseStats(
                total_courses=analytics["total_courses"],
                course_titles=analytics["course_titles"]
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/", response_model=Dict[str, str])
    async def root():
        """Root endpoint for health check"""
        return {"status": "ok", "message": "RAG API is running"}

    return TestClient(app)


@pytest.fixture
def sample_course():
    """Create a sample course for testing."""
    return Course(
        title="Introduction to Python",
        course_link="https://example.com/python",
        instructor="John Doe",
        lessons=[
            Lesson(lesson_number=1, title="Getting Started", lesson_link="https://example.com/lesson1"),
            Lesson(lesson_number=2, title="Data Types", lesson_link="https://example.com/lesson2"),
        ]
    )


@pytest.fixture
def sample_chunks():
    """Create sample course chunks for testing."""
    return [
        CourseChunk(
            content="Python is a high-level programming language.",
            course_title="Introduction to Python",
            lesson_number=1,
            chunk_index=0
        ),
        CourseChunk(
            content="Variables are containers for storing data values.",
            course_title="Introduction to Python",
            lesson_number=1,
            chunk_index=1
        ),
        CourseChunk(
            content="Python has several data types including strings, numbers, and lists.",
            course_title="Introduction to Python",
            lesson_number=2,
            chunk_index=0
        ),
    ]


@pytest.fixture
def mock_session_manager():
    """Create a mock session manager."""
    mock = MagicMock()
    mock.create_session.return_value = "test-session-123"
    mock.get_conversation_history.return_value = []
    mock.add_exchange = MagicMock()
    return mock


@pytest.fixture
def mock_vector_store():
    """Create a mock vector store."""
    mock = MagicMock()
    mock.search_content.return_value = [
        {"content": "Test content", "course": "Test Course", "score": 0.95}
    ]
    mock.get_course_count.return_value = 2
    mock.get_existing_course_titles.return_value = ["Course 1", "Course 2"]
    return mock


@pytest.fixture
def mock_ai_generator():
    """Create a mock AI generator."""
    mock = MagicMock()
    mock.generate_response.return_value = "This is a test response from the AI."
    return mock
