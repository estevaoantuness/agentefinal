# Test Suite for Pangeia Bot

Comprehensive test suites for all new features: command matching, response cleaning, function call parsing, and user personalization.

## Test Files

### 1. `test_command_matcher.py` (67 tests)
**Tests the NLP-like command pattern matching system.**

#### Test Coverage:
- **View Tasks**: 8 tests for different Portuguese variations and filters
- **Create Task**: 7 tests for task creation with various formats
- **Mark Done**: 8 tests for marking tasks as completed
- **Mark Progress**: 6 tests for marking tasks as in progress
- **View Progress**: 5 tests for viewing progress reports
- **Get Help**: 5 tests for help command
- **Edge Cases**: 12 tests for robustness
- **Estevao-Specific**: 2 test groups for real-world scenarios

#### Key Scenarios:
- Simple command variations in Portuguese
- Task numbers extraction (single and multiple)
- Status filters (pending, in_progress, completed)
- Case insensitivity and special characters
- Very long messages and unicode content
- Empty inputs and invalid formats

**Run**: `pytest test_command_matcher.py -v`

---

### 2. `test_webhooks_functions.py` (60+ tests)
**Tests webhook functions: response cleaning, function call parsing, integration workflows.**

#### Test Coverage:
- **Clean Response Text** (20 tests):
  - Removal of XML-style tags
  - Removal of arrow-style function calls
  - Removal of angle-bracket markers
  - Mixed format handling
  - Whitespace and special character handling

- **Parse Text Function Call** (25 tests):
  - Arrow format parsing
  - XML format parsing
  - Edge cases and malformed input
  - Multiple function calls
  - Real Groq response scenarios

- **Integration Tests** (3 tests):
  - Complete workflow: extract → clean
  - Multiple format cleanup
  - Display text generation

#### Key Scenarios:
- Groq LLaMA response format handling
- Function call display bug scenarios
- Fallback parsing when tool_calls unavailable
- User never sees function syntax
- Real-world Estevao conversation flows

**Run**: `pytest test_webhooks_functions.py -v`

---

### 3. `test_personalization.py` (50+ tests)
**Tests system prompt personalization and conversation management with user context.**

#### Test Coverage:
- **System Prompt Personalization** (12 tests):
  - Default prompts (no name)
  - Personalized prompts with various names
  - Special characters and long names
  - Estevao-specific scenarios

- **Conversation Manager** (15 tests):
  - Conversation creation with/without user name
  - User context injection
  - Message history preservation
  - Function result handling
  - Multi-user isolation

- **Edge Cases** (8 tests):
  - None/empty/whitespace names
  - Type safety (int, bool, list inputs)
  - Script injection attempts
  - SQL injection attempts
  - Problematic user IDs

- **Concurrency Tests** (5 tests):
  - Multiple users with concurrent conversations
  - Interleaved message adding
  - User isolation verification

#### Key Scenarios:
- Estevao personalization flow (greeting by name)
- Complete task workflow with personalization
- Conversation timeout and recreation
- Multiple simultaneous users
- System safety with malicious input

**Run**: `pytest test_personalization.py -v`

---

## Running the Tests

### Prerequisites
```bash
pip install pytest pytest-cov
```

### Run All Tests
```bash
pytest tests/ -v
```

### Run Specific Test File
```bash
pytest tests/test_command_matcher.py -v
pytest tests/test_webhooks_functions.py -v
pytest tests/test_personalization.py -v
```

### Run Specific Test Class
```bash
pytest tests/test_command_matcher.py::TestCommandMatcher -v
pytest tests/test_webhooks_functions.py::TestCleanResponseText -v
```

### Run Specific Test
```bash
pytest tests/test_command_matcher.py::TestCommandMatcher::test_view_tasks_simple_variation_1 -v
```

### With Coverage Report
```bash
pytest tests/ --cov=src --cov-report=html
# Open htmlcov/index.html in browser
```

### Run Only Estevao-Specific Tests
```bash
pytest tests/ -k "estevao" -v
```

---

## Test Organization

Each test file follows the **AAA Pattern** (Arrange-Act-Assert):

```python
def test_something(self):
    # Arrange: Setup test data
    message = "minhas tarefas"

    # Act: Execute the code
    result = self.matcher.match(message)

    # Assert: Verify the results
    assert result is not None
    assert result['function'] == 'view_tasks'
```

---

## Coverage Targets

- **Command Matcher**: 95%+ coverage
- **Webhook Functions**: 90%+ coverage
- **Personalization**: 85%+ coverage
- **Overall**: 85%+ code coverage

---

## Key Test Scenarios for Estevao

### Scenario 1: User Greeting
```
Message: "oi"
Expected: Bot responds with personalized greeting using Estevao's name
```

### Scenario 2: Task Listing
```
Message: "minhas tarefas"
Expected: Command matcher directly matches, executes view_tasks function
```

### Scenario 3: Task Creation
```
Message: "criar tarefa: Implementar login"
Expected: Title extracted correctly, function call cleaned from response
```

### Scenario 4: Function Call Cleanup
```
Groq Response: "=view_tasks>{\"filter_status\": \"all\"}"
Expected: Function syntax removed, message shows clean text only
```

### Scenario 5: Personalization
```
All Messages: Bot refers to Estevao by name throughout conversation
Expected: System prompt injected with "Estevão" personalization
```

---

## Local Testing Before Deployment

### Quick Validation Script
```bash
# Run minimal test suite
pytest tests/ -k "estevao" -v --tb=short
```

### Manual Testing in Docker
```bash
# In Docker container with bot running
curl -X POST http://localhost:8000/webhook/evolution \
  -H "Content-Type: application/json" \
  -d '{
    "event": "messages.upsert",
    "data": {
      "key": {"remoteJid": "5511987654321@s.whatsapp.net", "fromMe": false},
      "message": {"conversation": "minhas tarefas"},
      "pushName": "Estevão"
    }
  }'
```

---

## Common Issues & Debugging

### Import Errors
```bash
# Ensure PYTHONPATH includes project root
export PYTHONPATH="${PYTHONPATH}:/path/to/agente_pangeia_final"
pytest tests/
```

### Database Connection in Tests
Database mocking is not fully implemented in unit tests. For integration tests, ensure database is running or use SQLite for testing.

### Mock Setup Issues
Tests use `unittest.mock` for most dependencies. Verify mock patches match actual import paths.

---

## CI/CD Integration

Tests are designed to run in:
- Local development environment (before push)
- Docker container (during build)
- Render deployment pipeline (pre-deployment validation)

Add to your CI/CD pipeline:
```yaml
test:
  script:
    - pip install -r requirements.txt
    - pytest tests/ --cov=src --cov-report=term-missing
    - coverage report --fail-under=85
```

---

## Notes

- Tests are isolated and can run in any order
- No external API calls are made (all mocked)
- Tests are fast (< 5 seconds for entire suite)
- Tests verify both happy path and edge cases
- Tests emphasize real-world Estevao scenarios
