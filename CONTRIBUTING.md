# Contributing to VibeCraft

Thank you for your interest in contributing to VibeCraft! This guide will help you get started.

## Table of Contents

- [Development Setup](#development-setup)
- [Code Standards](#code-standards)
- [Pull Request Process](#pull-request-process)
- [Development Workflow](#development-workflow)
- [Testing](#testing)
- [Code Review](#code-review)
- [Questions?](#questions)

## Development Setup

### Prerequisites

- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) - Fast Python package manager
- Git
- Java 21 (for building the client mod, Minecraft 1.21.x)
- jq (`brew install jq`)

### Getting Started

1. **Fork and clone**
   ```bash
   git clone https://github.com/YOUR-USERNAME/vibecraft.git
   cd vibecraft
   ```

2. **Install MCP server dependencies**
   ```bash
   cd mcp-server && uv sync && cd ..
   ```

3. **Choose your development approach:**

#### Option A: Client Mod (Recommended)

Best for testing with any Minecraft server, multiplayer, and WorldEdit features.

```bash
# Build the client mod
cd client-mod && ./build.sh 1.21.1 && cd ..

# Install in Prism Launcher (or your launcher):
# 1. Add Fabric to a 1.21.1 instance
# 2. Add Fabric API mod
# 3. Add build/release/vibecraft-client-*.jar

# In Minecraft, run: /vibecraft allow

# Start MCP server
cd mcp-server && ./start-vibecraft.sh
```

#### Option B: RCON Mode (Server-Only/Headless)

For CI, headless testing, or server-side automation without a client.

```bash
# This starts a Minecraft server in Docker with RCON
./setup-all.sh
```

4. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Code Standards

### Python Style

- **PEP 8**: Follow Python style guide
- **Formatting**: Use Black for code formatting
  ```bash
  cd mcp-server
  uv run black src/
  ```
- **Linting**: Use Ruff for linting
  ```bash
  uv run ruff check src/
  ```
- **Type Hints**: Add type hints to all functions
  ```bash
  uv run mypy src/
  ```

### Commit Messages

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add terrain analyzer tool
fix: correct block detection in spatial scan
docs: update README with new examples
refactor: extract pattern lookup base class
test: add tests for furniture placement
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Code Organization

- Keep files focused and under 500 lines
- Extract reusable code to utilities
- Follow existing patterns in the codebase
- Add docstrings to all functions and classes

**Example**:
```python
async def handle_example_tool(
    arguments: Dict[str, Any],
    rcon: RCONManager,
    config: VibeCraftConfig,
    logger_instance: logging.Logger
) -> List[TextContent]:
    """
    Handle example_tool MCP tool.

    Args:
        arguments: Tool arguments from AI
        rcon: RCON connection manager
        config: Server configuration
        logger_instance: Logger instance

    Returns:
        List of TextContent responses
    """
    # Implementation
    pass
```

## Pull Request Process

### Before Submitting

1. **Update documentation**
   - Add/update README.md if adding features
   - Update AGENTS.md if changing AI instructions
   - Add examples if helpful

2. **Run tests**
   ```bash
   cd mcp-server
   uv run pytest
   ```

3. **Format code**
   ```bash
   uv run black src/
   uv run ruff check --fix src/
   ```

4. **Verify changes**
   - Test your changes with actual AI client
   - Ensure no regressions
   - Check all files are committed

### Submitting PR

1. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create Pull Request**
   - Visit your fork on GitHub
   - Click "New Pull Request"
   - Fill out PR template with:
     - Clear description of changes
     - Why the change is needed
     - Testing performed
     - Screenshots/examples if applicable

3. **PR Title**
   ```
   feat: add spatial awareness v2 system
   fix: correct furniture placement offset
   docs: improve setup instructions
   ```

### PR Checklist

- [ ] Code follows style guide (Black, Ruff, MyPy)
- [ ] All tests pass
- [ ] Documentation updated
- [ ] No breaking changes (or clearly documented)
- [ ] Commit messages follow conventional commits
- [ ] PR description is clear and complete

## Development Workflow

### Branch Strategy

- **main** - Stable releases only
- **develop** - Active development (not currently used, submit to main)
- **feature/*** - New features
- **fix/*** - Bug fixes
- **docs/*** - Documentation updates

### Making Changes

1. **Start from main**
   ```bash
   git checkout main
   git pull upstream main
   ```

2. **Create feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```

3. **Make changes**
   - Write code
   - Add tests
   - Update docs

4. **Test locally**
   ```bash
   cd mcp-server
   uv run pytest
   uv run python -m src.vibecraft.server  # Test server starts
   ```

5. **Commit changes**
   ```bash
   git add .
   git commit -m "feat: add amazing feature"
   ```

6. **Push and create PR**

## Testing

### Running Tests

```bash
cd mcp-server

# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src/vibecraft --cov-report=html

# Run specific test file
uv run pytest tests/test_spatial.py

# Run with verbose output
uv run pytest -v
```

### Writing Tests

Add tests for new features in `mcp-server/tests/`:

```python
import pytest
from src.vibecraft.example_module import ExampleClass

def test_example_function():
    """Test example function works correctly."""
    result = ExampleClass().example_method()
    assert result == expected_value
```

### Manual Testing

1. **Start MCP server**
   ```bash
   cd mcp-server
   uv run python -m src.vibecraft.server
   ```

2. **Test with AI client**
   - Claude Code
   - Claude Desktop
   - Cursor

3. **Verify functionality**
   - Test new tools work
   - Check edge cases
   - Ensure no regressions

## Code Review

All submissions require review. We'll:

1. **Check code quality**
   - Follows style guide
   - Well-organized and readable
   - Proper error handling

2. **Verify tests pass**
   - All existing tests pass
   - New features have tests
   - Good test coverage

3. **Ensure docs are updated**
   - README reflects changes
   - SYSTEM_PROMPT updated if needed
   - Examples added if helpful

4. **Test functionality**
   - Changes work as described
   - No breaking changes
   - Performance is acceptable

### Review Timeline

- **Initial review**: Within 3 days
- **Follow-up**: Within 2 days
- **Merge**: Once approved and CI passes

## Questions?

- **Issues**: Open an [issue](https://github.com/amenti-labs/vibecraft/issues) for bugs or feature requests
- **Discussions**: Use [GitHub Discussions](https://github.com/amenti-labs/vibecraft/discussions) for questions
- **Security**: Email security concerns to [security contact]

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to VibeCraft!** 🎮✨
