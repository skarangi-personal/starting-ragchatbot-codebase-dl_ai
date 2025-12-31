# Testing Quick Start Guide

## Installation

```bash
uv sync --all-extras
```

This installs pytest, pytest-cov, and other test dependencies.

## Running Tests

### Run all tests
```bash
uv run pytest
```

### Run with verbose output
```bash
uv run pytest -v
```

### Run specific test file
```bash
uv run pytest backend/tests/test_api_endpoints.py
```

### Run specific test class
```bash
uv run pytest backend/tests/test_api_endpoints.py::TestQueryEndpoint
```

### Run specific test function
```bash
uv run pytest backend/tests/test_api_endpoints.py::TestQueryEndpoint::test_query_with_session_id
```

### Run with coverage report
```bash
uv run pytest --cov=backend --cov-report=html
open htmlcov/index.html
```

## Test Files

| File | Tests | Purpose |
|------|-------|---------|
| `test_api_endpoints.py` | 25 | FastAPI endpoint testing |
| `test_models.py` | 17 | Pydantic model validation |
| `test_components.py` | 18 | Component unit tests |
| `conftest.py` | - | Shared fixtures |

## Available Fixtures

Use these in your test functions:

### `test_client`
FastAPI TestClient for HTTP requests
```python
def test_something(test_client):
    response = test_client.get("/api/courses")
    assert response.status_code == 200
```

### `mock_rag_system`
Mocked RAG system with configurable responses
```python
def test_query(test_client, mock_rag_system):
    mock_rag_system.query.return_value = ("answer", [])
    # ... test code
```

### `test_config`
Configuration with temporary database
```python
def test_config_usage(test_config):
    assert test_config.CHROMA_PATH != ""
```

### `sample_course`
Pre-built Course object
```python
def test_course_data(sample_course):
    assert sample_course.title == "Introduction to Python"
```

### `sample_chunks`
Pre-built CourseChunk objects
```python
def test_chunks(sample_chunks):
    assert len(sample_chunks) == 3
```

### Mock Fixtures
- `mock_session_manager`
- `mock_vector_store`
- `mock_ai_generator`

## Writing a New Test

```python
def test_new_feature(test_client, mock_rag_system):
    """Test description"""
    # Arrange - setup mock behavior
    mock_rag_system.query.return_value = ("answer", [])

    # Act - make request
    response = test_client.post(
        "/api/query",
        json={"query": "test"}
    )

    # Assert - verify response
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
```

## Common Patterns

### Testing Query Endpoint
```python
response = test_client.post(
    "/api/query",
    json={"query": "What is Python?", "session_id": "abc123"}
)
assert response.status_code == 200
```

### Testing Courses Endpoint
```python
response = test_client.get("/api/courses")
assert response.status_code == 200
data = response.json()
assert "total_courses" in data
```

### Mocking Errors
```python
mock_rag_system.query.side_effect = Exception("Test error")
response = test_client.post("/api/query", json={"query": "test"})
assert response.status_code == 500
```

### Mocking Model Data
```python
from models import Course, Lesson

course = Course(
    title="Test",
    lessons=[Lesson(lesson_number=1, title="Intro")]
)
```

## Test Organization

```
backend/tests/
├── conftest.py              # Fixtures (never modify directly)
├── test_api_endpoints.py    # Add API tests here
├── test_models.py           # Add model tests here
├── test_components.py       # Add component tests here
└── README.md                # Full documentation
```

## Test Results

All 60 tests should pass:
```
===================== 60 passed in 48.30s =======================
```

If tests fail:
1. Check Python version: `python3 --version` (should be 3.13+)
2. Reinstall dependencies: `uv sync --all-extras`
3. Review error message and fixture availability

## Coverage Goals

Generate coverage report:
```bash
uv run pytest --cov=backend --cov-report=html
```

Current coverage:
- Models: 100%
- Config: 100%
- Test code: 100%
- Overall: 56% (some components use mocks)

## Tips

1. **Use descriptive test names** that explain what's being tested
2. **One assertion per concept** - keep tests focused
3. **Use fixtures** - don't create test data manually
4. **Mock external dependencies** - tests should be fast and isolated
5. **Test edge cases** - empty inputs, missing fields, large data
6. **Run tests frequently** - during development

## Troubleshooting

### Import Errors
- Ensure you're in the project root
- Tests add backend to sys.path automatically

### Fixture Not Found
- Check spelling against conftest.py
- Reload IDE if you just added a fixture

### Tests Timeout
- Mocks should return instantly
- If tests are slow, check for network/file I/O

### Coverage Too Low
- Focus on testing business logic, not implementation details
- Use mocks to avoid testing dependencies

## Next Steps

1. Run: `uv run pytest -v`
2. Review: `backend/tests/README.md` for detailed docs
3. Add: New tests as features are developed
4. Monitor: Coverage with `--cov` reports

---

**Full documentation**: See `backend/tests/README.md`
