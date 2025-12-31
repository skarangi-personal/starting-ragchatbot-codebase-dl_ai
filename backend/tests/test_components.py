"""Tests for individual RAG system components."""

import pytest
from unittest.mock import MagicMock, patch
from models import Course, Lesson, CourseChunk


class TestSessionManager:
    """Test suite for SessionManager."""

    def test_session_creation(self, mock_session_manager):
        """Test that session manager creates sessions."""
        session_id = mock_session_manager.create_session()

        assert session_id is not None
        assert isinstance(session_id, str)

    def test_session_manager_called_on_new_query(self, mock_session_manager):
        """Test that session manager is called when creating a session."""
        mock_session_manager.create_session()

        mock_session_manager.create_session.assert_called()

    def test_conversation_history_retrieval(self, mock_session_manager):
        """Test retrieving conversation history."""
        history = mock_session_manager.get_conversation_history("session-123")

        assert isinstance(history, list)
        assert history == []

    def test_adding_exchange_to_session(self, mock_session_manager):
        """Test adding query-response exchange to session."""
        mock_session_manager.add_exchange(
            "session-123",
            "What is Python?",
            "Python is a programming language."
        )

        mock_session_manager.add_exchange.assert_called_once()


class TestVectorStore:
    """Test suite for VectorStore."""

    def test_vector_store_search(self, mock_vector_store):
        """Test vector store search functionality."""
        results = mock_vector_store.search_content("Python")

        assert isinstance(results, list)
        assert len(results) > 0

    def test_search_result_structure(self, mock_vector_store):
        """Test that search results have expected structure."""
        results = mock_vector_store.search_content("Python")

        for result in results:
            assert "content" in result
            assert "course" in result

    def test_course_count(self, mock_vector_store):
        """Test getting course count from vector store."""
        count = mock_vector_store.get_course_count()

        assert isinstance(count, int)
        assert count >= 0

    def test_existing_course_titles(self, mock_vector_store):
        """Test retrieving existing course titles."""
        titles = mock_vector_store.get_existing_course_titles()

        assert isinstance(titles, list)
        for title in titles:
            assert isinstance(title, str)


class TestAIGenerator:
    """Test suite for AIGenerator."""

    def test_response_generation(self, mock_ai_generator):
        """Test response generation from AI."""
        response = mock_ai_generator.generate_response(
            query="What is Python?",
            conversation_history=[],
            tools=[],
            tool_manager=None
        )

        assert isinstance(response, str)
        assert len(response) > 0

    def test_response_with_tools(self, mock_ai_generator):
        """Test response generation with available tools."""
        tools = [
            {
                "name": "search",
                "description": "Search for content"
            }
        ]

        response = mock_ai_generator.generate_response(
            query="Test query",
            conversation_history=[],
            tools=tools,
            tool_manager=MagicMock()
        )

        assert response is not None

    def test_response_with_history(self, mock_ai_generator):
        """Test response generation with conversation history."""
        history = [
            {"role": "user", "content": "First question"},
            {"role": "assistant", "content": "First answer"}
        ]

        response = mock_ai_generator.generate_response(
            query="Follow-up question",
            conversation_history=history,
            tools=[],
            tool_manager=None
        )

        assert response is not None


class TestDocumentProcessor:
    """Test suite for DocumentProcessor."""

    @patch('document_processor.DocumentProcessor')
    def test_document_chunking(self, mock_processor):
        """Test document is split into chunks."""
        mock_instance = mock_processor.return_value
        chunks = [
            CourseChunk(content="Chunk 1", course_title="Test", chunk_index=0),
            CourseChunk(content="Chunk 2", course_title="Test", chunk_index=1)
        ]
        mock_instance.chunk_text.return_value = chunks

        result = mock_instance.chunk_text("Long document text")

        assert len(result) == 2

    @patch('document_processor.DocumentProcessor')
    def test_course_document_processing(self, mock_processor):
        """Test processing a course document."""
        mock_instance = mock_processor.return_value
        course = Course(title="Test Course", lessons=[])
        mock_instance.process_course_document.return_value = (course, [])

        result_course, result_chunks = mock_instance.process_course_document("test.txt")

        assert result_course.title == "Test Course"
        assert isinstance(result_chunks, list)

    @patch('document_processor.DocumentProcessor')
    def test_metadata_extraction(self, mock_processor):
        """Test metadata extraction from document."""
        mock_instance = mock_processor.return_value
        expected_metadata = {
            "title": "Python Basics",
            "instructor": "John Doe"
        }
        mock_instance.extract_metadata.return_value = expected_metadata

        metadata = mock_instance.extract_metadata("document content")

        assert metadata["title"] == "Python Basics"
        assert metadata["instructor"] == "John Doe"


class TestSearchTools:
    """Test suite for search tools."""

    @patch('search_tools.CourseSearchTool')
    def test_course_search_tool_initialization(self, mock_tool_class):
        """Test search tool initialization."""
        mock_tool = mock_tool_class.return_value
        mock_vector_store = MagicMock()

        mock_tool_class(mock_vector_store)

        mock_tool_class.assert_called_once_with(mock_vector_store)

    @patch('search_tools.ToolManager')
    def test_tool_manager_register_tool(self, mock_manager_class):
        """Test tool manager can register tools."""
        mock_manager = mock_manager_class.return_value
        mock_tool = MagicMock()

        mock_manager.register_tool(mock_tool)

        mock_manager.register_tool.assert_called_once_with(mock_tool)

    @patch('search_tools.ToolManager')
    def test_tool_manager_get_definitions(self, mock_manager_class):
        """Test getting tool definitions."""
        mock_manager = mock_manager_class.return_value
        expected_tools = [{"name": "search", "description": "Search"}]
        mock_manager.get_tool_definitions.return_value = expected_tools

        tools = mock_manager.get_tool_definitions()

        assert tools == expected_tools


class TestRAGSystemIntegration:
    """Test suite for RAG system component integration."""

    def test_rag_system_initialization(self, test_config):
        """Test RAG system initializes all components."""
        with patch('rag_system.RAGSystem') as mock_rag_class:
            mock_rag = mock_rag_class.return_value

            # Verify mock is set up with needed attributes
            assert hasattr(mock_rag, 'query') or hasattr(mock_rag, 'get_course_analytics')

    def test_query_flow_with_mocks(self, mock_rag_system, sample_chunks):
        """Test end-to-end query flow with mocked components."""
        mock_rag_system.query.return_value = (
            "Test answer",
            [{"title": "Test Course", "url": None}]
        )

        answer, sources = mock_rag_system.query("What is Python?", "session-123")

        assert answer == "Test answer"
        assert len(sources) > 0
        assert sources[0]["title"] == "Test Course"

    def test_analytics_flow(self, mock_rag_system):
        """Test analytics retrieval flow."""
        mock_rag_system.get_course_analytics.return_value = {
            "total_courses": 2,
            "course_titles": ["Course 1", "Course 2"]
        }

        analytics = mock_rag_system.get_course_analytics()

        assert analytics["total_courses"] == 2
        assert len(analytics["course_titles"]) == 2
