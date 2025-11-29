# Testing Guide

## Running Tests Locally

### Prerequisites
```bash
# Install test dependencies
pip install -r requirements.txt
```

### Run All Tests
```bash
# Using pytest directly
pytest

# With verbose output
pytest -v

# With coverage
pytest --cov

# Run specific test file
pytest tests/test_models.py

# Run specific test
pytest tests/test_health.py::TestHealthEndpoints::test_health_endpoint_success
```

### Run Tests in Docker
```bash
# Run all tests
docker-compose run --rm web pytest -v

# With coverage
docker-compose run --rm web pytest -v --cov --cov-report=html

# View coverage report
# Open htmlcov/index.html in your browser
```

## Test Structure

```
tests/
├── __init__.py
├── conftest.py          # Pytest fixtures
├── test_health.py       # Health endpoint tests
├── test_models.py       # Model tests
├── test_api.py          # API endpoint tests
└── test_tools.py        # Tool registry tests
```

## Test Categories

### Unit Tests
- Model creation and methods
- Service layer logic
- Tool registry functionality

### Integration Tests
- API endpoints
- Database operations
- WebSocket connections (when added)

### Health Check Tests
- `/health/` endpoint
- `/ready/` readiness probe

## Writing New Tests

### Example Test
```python
import pytest
from rag.models import Document

@pytest.mark.django_db
class TestMyFeature:
    def test_something(self, api_client):
        # Arrange
        doc = Document.objects.create(title="Test", content="Content")
        
        # Act
        response = api_client.get(f'/api/rag/documents/{doc.id}/')
        
        # Assert
        assert response.status_code == 200
```

### Using Fixtures
```python
def test_with_document(create_document):
    # create_document is a fixture from conftest.py
    doc = create_document(title="My Doc")
    assert doc.title == "My Doc"
```

## Coverage Reports

### Generate HTML Coverage Report
```bash
pytest --cov --cov-report=html
open htmlcov/index.html  # View in browser
```

### Coverage Threshold
Current coverage target: **80%+**

## Continuous Integration

Tests run automatically on:
- Every push to `main` or `develop`
- Every pull request
- Manual workflow dispatch

See `.github/workflows/ci.yml` for CI configuration.

## Troubleshooting

### Database Errors
Tests use SQLite in-memory database by default. If you see database errors:
```bash
# Clear test database
rm -f test_db.sqlite3
```

### Import Errors
Make sure you're in the project root:
```bash
cd /path/to/agentic_rag
pytest
```

### Slow Tests
```bash
# Run only fast tests
pytest -m "not slow"

# Run parallel tests
pytest -n auto  # (requires pytest-xdist)
```

## Test Markers

- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.slow` - Slow-running tests
- `@pytest.mark.django_db` - Tests requiring database

## Best Practices

1. **Isolate Tests**: Each test should be independent
2. **Use Fixtures**: Reuse setup code via fixtures
3. **Mock External APIs**: Don't make real API calls in tests
4. **Fast Tests**: Keep tests fast (< 1s each)
5. **Clear Names**: Test names should describe what they test
6. **Arrange-Act-Assert**: Follow AAA pattern

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [pytest-django](https://pytest-django.readthedocs.io/)
- [Django Testing](https://docs.djangoproject.com/en/stable/topics/testing/)
