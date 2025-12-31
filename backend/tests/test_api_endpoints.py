"""API endpoint tests for the FastAPI application."""

import pytest
from fastapi.testclient import TestClient


class TestQueryEndpoint:
    """Test suite for the /api/query endpoint."""

    def test_query_with_session_id(self, test_client):
        """Test query endpoint with existing session ID."""
        response = test_client.post(
            "/api/query",
            json={
                "query": "What is Python?",
                "session_id": "test-session-123"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert "sources" in data
        assert "session_id" in data
        assert data["session_id"] == "test-session-123"
        assert isinstance(data["sources"], list)

    def test_query_without_session_id(self, test_client):
        """Test query endpoint creates new session ID."""
        response = test_client.post(
            "/api/query",
            json={"query": "What is Python?"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert data["session_id"] == "session-123"
        assert "answer" in data
        assert "sources" in data

    def test_query_response_structure(self, test_client):
        """Test query response has correct structure."""
        response = test_client.post(
            "/api/query",
            json={"query": "Tell me about AI"}
        )

        assert response.status_code == 200
        data = response.json()

        # Validate response structure
        assert isinstance(data["answer"], str)
        assert len(data["answer"]) > 0
        assert isinstance(data["sources"], list)

        # Validate source structure
        for source in data["sources"]:
            assert "title" in source
            assert isinstance(source["title"], str)
            assert "url" in source or source["url"] is None

    def test_query_with_empty_query(self, test_client):
        """Test query endpoint with empty query string."""
        response = test_client.post(
            "/api/query",
            json={"query": ""}
        )

        # Should still return 200 as validation happens in business logic
        assert response.status_code == 200

    def test_query_with_long_query(self, test_client):
        """Test query endpoint with a very long query."""
        long_query = "What is Python? " * 100
        response = test_client.post(
            "/api/query",
            json={"query": long_query}
        )

        assert response.status_code == 200
        assert "session_id" in response.json()

    def test_query_invalid_json(self, test_client):
        """Test query endpoint with invalid JSON."""
        response = test_client.post(
            "/api/query",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )

        assert response.status_code == 422  # Unprocessable Entity

    def test_query_missing_required_field(self, test_client):
        """Test query endpoint with missing required query field."""
        response = test_client.post(
            "/api/query",
            json={"session_id": "test-session"}
        )

        assert response.status_code == 422  # Validation error

    def test_query_multiple_sequential_queries(self, test_client):
        """Test multiple sequential queries with same session."""
        session_id = None

        for i in range(3):
            response = test_client.post(
                "/api/query",
                json={
                    "query": f"Question {i}",
                    "session_id": session_id
                }
            )

            assert response.status_code == 200
            data = response.json()
            session_id = data["session_id"]
            assert session_id is not None

    def test_query_preserves_session_context(self, test_client):
        """Test that session context is maintained across queries."""
        # First query
        response1 = test_client.post(
            "/api/query",
            json={"query": "First question"}
        )
        session_id = response1.json()["session_id"]

        # Second query with same session
        response2 = test_client.post(
            "/api/query",
            json={
                "query": "Follow-up question",
                "session_id": session_id
            }
        )

        assert response2.status_code == 200
        assert response2.json()["session_id"] == session_id


class TestCoursesEndpoint:
    """Test suite for the /api/courses endpoint."""

    def test_courses_endpoint_returns_stats(self, test_client):
        """Test courses endpoint returns course statistics."""
        response = test_client.get("/api/courses")

        assert response.status_code == 200
        data = response.json()
        assert "total_courses" in data
        assert "course_titles" in data

    def test_courses_endpoint_response_structure(self, test_client):
        """Test courses response has correct structure."""
        response = test_client.get("/api/courses")

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data["total_courses"], int)
        assert data["total_courses"] >= 0
        assert isinstance(data["course_titles"], list)

    def test_courses_endpoint_course_titles_are_strings(self, test_client):
        """Test that all course titles are strings."""
        response = test_client.get("/api/courses")

        assert response.status_code == 200
        data = response.json()

        for title in data["course_titles"]:
            assert isinstance(title, str)
            assert len(title) > 0

    def test_courses_endpoint_count_matches_titles_list(self, test_client):
        """Test that total_courses matches length of course_titles list."""
        response = test_client.get("/api/courses")

        assert response.status_code == 200
        data = response.json()

        assert data["total_courses"] == len(data["course_titles"])

    def test_courses_endpoint_multiple_calls_consistent(self, test_client):
        """Test that multiple calls to courses endpoint return consistent data."""
        response1 = test_client.get("/api/courses")
        response2 = test_client.get("/api/courses")

        assert response1.status_code == 200
        assert response2.status_code == 200

        data1 = response1.json()
        data2 = response2.json()

        assert data1["total_courses"] == data2["total_courses"]
        assert data1["course_titles"] == data2["course_titles"]

    def test_courses_endpoint_with_no_courses(self, test_client, mock_rag_system):
        """Test courses endpoint when no courses are loaded."""
        # Mock no courses scenario
        mock_rag_system.get_course_analytics.return_value = {
            "total_courses": 0,
            "course_titles": []
        }

        response = test_client.get("/api/courses")

        assert response.status_code == 200
        data = response.json()
        assert data["total_courses"] == 0
        assert data["course_titles"] == []

    def test_courses_endpoint_with_many_courses(self, test_client, mock_rag_system):
        """Test courses endpoint with many courses."""
        # Mock many courses
        course_titles = [f"Course {i}" for i in range(100)]
        mock_rag_system.get_course_analytics.return_value = {
            "total_courses": 100,
            "course_titles": course_titles
        }

        response = test_client.get("/api/courses")

        assert response.status_code == 200
        data = response.json()
        assert data["total_courses"] == 100
        assert len(data["course_titles"]) == 100


class TestRootEndpoint:
    """Test suite for the root endpoint."""

    def test_root_endpoint_exists(self, test_client):
        """Test root endpoint returns 200."""
        response = test_client.get("/")

        assert response.status_code == 200

    def test_root_endpoint_response_structure(self, test_client):
        """Test root endpoint response structure."""
        response = test_client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "message" in data

    def test_root_endpoint_response_content(self, test_client):
        """Test root endpoint response contains expected values."""
        response = test_client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "RAG API" in data["message"]


class TestErrorHandling:
    """Test suite for error handling in API endpoints."""

    def test_query_error_returns_500(self, test_client, mock_rag_system):
        """Test query endpoint returns 500 on error."""
        # Mock an exception
        mock_rag_system.query.side_effect = Exception("Test error")

        response = test_client.post(
            "/api/query",
            json={"query": "Test query"}
        )

        assert response.status_code == 500
        assert "detail" in response.json()

    def test_courses_error_returns_500(self, test_client, mock_rag_system):
        """Test courses endpoint returns 500 on error."""
        # Mock an exception
        mock_rag_system.get_course_analytics.side_effect = Exception("Test error")

        response = test_client.get("/api/courses")

        assert response.status_code == 500
        assert "detail" in response.json()

    def test_error_message_is_string(self, test_client, mock_rag_system):
        """Test error messages are returned as strings."""
        mock_rag_system.query.side_effect = Exception("Custom error message")

        response = test_client.post(
            "/api/query",
            json={"query": "Test"}
        )

        assert response.status_code == 500
        error_detail = response.json()["detail"]
        assert isinstance(error_detail, str)
        assert "Custom error message" in error_detail


class TestContentTypes:
    """Test suite for content type handling."""

    def test_json_response_content_type(self, test_client):
        """Test endpoints return JSON content type."""
        response = test_client.get("/api/courses")

        assert response.headers["content-type"] == "application/json"

    def test_query_accepts_json(self, test_client):
        """Test query endpoint accepts JSON content."""
        response = test_client.post(
            "/api/query",
            json={"query": "Test"},
            headers={"Content-Type": "application/json"}
        )

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"

    def test_query_rejects_form_data(self, test_client):
        """Test query endpoint rejects form data."""
        response = test_client.post(
            "/api/query",
            data={"query": "Test"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )

        # Form data won't match the JSON schema
        assert response.status_code == 422
