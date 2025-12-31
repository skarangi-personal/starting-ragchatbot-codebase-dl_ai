# RAG System Testing Framework

This directory contains the comprehensive testing framework for the Course Materials RAG System. The framework provides complete test coverage for API endpoints, models, and system components with proper isolation through fixtures and mocks.

## Overview

The testing framework includes:

- **API Endpoint Tests** - Full HTTP request/response testing for all FastAPI endpoints
- **Model Tests** - Validation tests for Pydantic models
- **Component Tests** - Unit tests for individual system components
- **Shared Fixtures** - Reusable test data and mock objects
- **pytest Configuration** - Organized test discovery and reporting

## Setup

### Install Test Dependencies

```bash
uv sync --all-extras
# or
uv add --group dev pytest pytest-cov httpx
```

### Key Test Dependencies

- **pytest** (7.4.3) - Test framework
- **pytest-cov** (4.1.0) - Code coverage reporting
- **httpx** (0.25.2) - HTTP client (bundled with TestClient)

## Running Tests

### Run All Tests

```bash
uv run pytest
```

### Run Specific Test File

```bash
uv run pytest backend/tests/test_api_endpoints.py
```

### Run Specific Test Class

```bash
uv run pytest backend/tests/test_api_endpoints.py::TestQueryEndpoint
```

### Run Specific Test Function

```bash
uv run pytest backend/tests/test_api_endpoints.py::TestQueryEndpoint::test_query_with_session_id
```

### Run Tests with Verbose Output

```bash
uv run pytest -v
```

### Run Tests by Marker

```bash
# Run only API tests
uv run pytest -m api

# Run only unit tests
uv run pytest -m unit

# Run only integration tests
uv run pytest -m integration
```

### Generate Coverage Report

```bash
uv run pytest --cov=backend --cov-report=html
```

This generates an HTML coverage report in `htmlcov/index.html`

### Run Tests in Watch Mode (requires pytest-watch)

```bash
uv add --group dev pytest-watch
uv run ptw
```

## Test Organization

### File Structure

```
backend/tests/
├── __init__.py                 # Package marker
├── conftest.py                 # Shared fixtures and configuration
├── README.md                   # This file
├── test_api_endpoints.py       # API endpoint tests
├── test_models.py              # Pydantic model tests
└── test_components.py          # Component unit tests
```

### Test File Conventions

- Test files start with `test_` prefix
- Test classes start with `Test` prefix
- Test functions start with `test_` prefix
- Each test class focuses on one component or endpoint

## Fixtures

All fixtures are defined in `conftest.py` and are automatically available to all tests.

### Core Fixtures

#### `test_client`
FastAPI TestClient with mocked RAG system and no static file mounting.

```python
def test_example(test_client):
    response = test_client.get("/api/courses")
    assert response.status_code == 200
```

#### `mock_rag_system`
Fully mocked RAG system with pre-configured return values.

```python
def test_with_mock(mock_rag_system):
    mock_rag_system.query.return_value = ("answer", [])
    # Your test code
```

#### `test_config`
Test configuration with temporary ChromaDB path.

```python
def test_config_usage(test_config):
    assert test_config.CHROMA_PATH != ""  # Temporary directory
```

#### `sample_course`
Pre-configured Course object with lessons.

```python
def test_with_sample_course(sample_course):
    assert sample_course.title == "Introduction to Python"
```

#### `sample_chunks`
Sample CourseChunk objects for testing content processing.

```python
def test_with_chunks(sample_chunks):
    assert len(sample_chunks) == 3
```

### Mock Fixtures

- `mock_rag_system` - Mocked RAG orchestrator
- `mock_session_manager` - Mocked session management
- `mock_vector_store` - Mocked vector search
- `mock_ai_generator` - Mocked AI response generation

## Test Structure

### API Endpoint Tests (`test_api_endpoints.py`)

Comprehensive tests for FastAPI endpoints organized by endpoint.

#### QueryEndpoint Tests
- `test_query_with_session_id` - Query with existing session
- `test_query_without_session_id` - Auto-creates new session
- `test_query_response_structure` - Validates response format
- `test_query_error_handling` - Tests error scenarios
- `test_query_multiple_sequential_queries` - Session persistence
- `test_query_preserves_session_context` - Context across queries

#### CoursesEndpoint Tests
- `test_courses_endpoint_returns_stats` - Returns course statistics
- `test_courses_endpoint_response_structure` - Valid response format
- `test_courses_endpoint_count_matches_titles` - Data consistency
- `test_courses_endpoint_with_no_courses` - Empty dataset handling
- `test_courses_endpoint_with_many_courses` - Large dataset handling

#### RootEndpoint Tests
- `test_root_endpoint_exists` - Health check
- `test_root_endpoint_response_structure` - Response format validation

#### Error Handling Tests
- `test_query_error_returns_500` - Exception handling
- `test_courses_error_returns_500` - Exception handling
- `test_error_message_is_string` - Error format validation

### Model Tests (`test_models.py`)

Validation and serialization tests for Pydantic models.

#### Lesson Model Tests
- Creation with all fields
- Creation with optional fields
- Model validation

#### Course Model Tests
- Full course creation
- Minimal required fields
- Nested lesson objects

#### CourseChunk Model Tests
- Chunk creation with all fields
- Optional lesson_number handling
- Long content support
- Model validation

### Component Tests (`test_components.py`)

Unit tests for individual system components with mocking.

#### SessionManager Tests
- Session creation
- History retrieval
- Exchange recording

#### VectorStore Tests
- Search functionality
- Course count retrieval
- Title listing

#### AIGenerator Tests
- Response generation
- Tool integration
- History handling

#### DocumentProcessor Tests
- Chunking logic
- Metadata extraction
- Course processing

#### SearchTools Tests
- Tool initialization
- Tool registration
- Definition retrieval

## Test Data and Mocking

### Mocking Strategy

Tests use `unittest.mock` for isolation:

- **Fixtures** mock expensive/external resources
- **Patches** override specific functions during tests
- **TestClient** simulates HTTP requests without running server
- **Temporary directories** isolate ChromaDB instances

### Example Mock Usage

```python
def test_query_with_mock_response(mock_rag_system):
    # Configure mock behavior
    mock_rag_system.query.return_value = (
        "Custom answer",
        [{"title": "Course", "url": "https://example.com"}]
    )

    # Test code using mocked system
    response = test_client.post("/api/query", json={"query": "test"})
    assert response.status_code == 200
```

## Pytest Configuration

Configuration is in `pyproject.toml` under `[tool.pytest.ini_options]`:

```toml
[tool.pytest.ini_options]
testpaths = ["backend/tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = ["-v", "--tb=short", "--cov=backend"]
markers = [
    "unit: mark test as a unit test",
    "integration: mark test as an integration test",
    "api: mark test as an API test",
]
```

### Configuration Options

- `testpaths` - Directories to search for tests
- `python_files` - File name patterns for test discovery
- `python_classes` - Class name patterns for test discovery
- `python_functions` - Function name patterns for test discovery
- `addopts` - Default command line options
- `markers` - Custom test markers for categorization

## Best Practices

### Writing New Tests

1. **Organize by component** - Group related tests in classes
2. **Use descriptive names** - Test names should describe what they test
3. **One assertion per concept** - Keep tests focused
4. **Use fixtures** - Leverage existing fixtures for consistency
5. **Mock external dependencies** - Use mocks for API calls, DB, etc.

### Test Example

```python
class TestFeature:
    """Test suite for new feature"""

    def test_feature_happy_path(self, test_client, mock_rag_system):
        """Test feature works with valid input"""
        response = test_client.post(
            "/api/endpoint",
            json={"param": "value"}
        )

        assert response.status_code == 200
        assert "expected_field" in response.json()

    def test_feature_error_handling(self, test_client, mock_rag_system):
        """Test feature handles errors gracefully"""
        mock_rag_system.method.side_effect = Exception("Error")

        response = test_client.post(
            "/api/endpoint",
            json={"param": "value"}
        )

        assert response.status_code == 500
```

### Adding New Fixtures

Add fixtures to `conftest.py`:

```python
@pytest.fixture
def my_custom_fixture():
    """Description of fixture"""
    # Setup
    data = {"key": "value"}

    yield data  # Provide to tests

    # Teardown (optional)
```

## Static File Handling

The test framework avoids static file mounting issues by:

1. **Creating a test app** in `conftest.py` without static file mounting
2. **Inlining API endpoints** in test app for isolation
3. **Using TestClient** which simulates HTTP without actual file serving
4. **Avoiding dependency on frontend files** for backend tests

This approach ensures tests don't fail due to missing `../frontend` directory.

## Continuous Integration

For CI/CD pipelines, run:

```bash
uv run pytest --cov=backend --cov-report=xml --junitxml=test-results.xml
```

This generates:
- XML coverage report for tools like Codecov
- JUnit XML for CI/CD integration
- Terminal output with test results

## Common Issues and Solutions

### Import Errors

**Problem**: `ModuleNotFoundError` for backend modules

**Solution**: Fixtures automatically add backend to sys.path. Ensure tests are in `backend/tests/`.

### Fixture Not Found

**Problem**: `fixture 'my_fixture' not found`

**Solution**: Fixtures must be in `conftest.py` or imported from it. Check spelling.

### Static Files Not Found

**Problem**: `FileNotFoundError` for frontend files

**Solution**: Tests use mocked app without static mounting. Use `test_client` fixture instead.

### Tests Pass Locally but Fail in CI

**Problem**: Environment differences

**Solution**: Ensure `uv.lock` is committed and use `uv sync` for consistent environments.

## Coverage Goals

Current test coverage targets:

- API Endpoints: 90%+
- Models: 100%
- Components (with mocks): 80%+

Generate report:

```bash
uv run pytest --cov=backend --cov-report=html
open htmlcov/index.html  # macOS
```

## Future Enhancements

Possible test framework improvements:

- Integration tests with real ChromaDB instances
- Performance/load testing with locust
- Snapshot testing for response validation
- Parameterized tests for edge cases
- E2E tests with browser automation (Playwright)
- Database fixture factories for complex test data

## Contributing

When adding new features:

1. Write tests first (TDD approach recommended)
2. Organize tests by component
3. Use existing fixtures where possible
4. Add fixtures only if reused across multiple tests
5. Document complex test scenarios
6. Maintain >80% code coverage

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [unittest.mock Documentation](https://docs.python.org/3/library/unittest.mock.html)
- [FastAPI Testing](https://fastapi.tiangolo.com/advanced/testing-dependencies/)
- [Pydantic Model Testing](https://docs.pydantic.dev/latest/concepts/validators/)
