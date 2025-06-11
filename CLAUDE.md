# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a Python implementation of frame-based knowledge representation systems inspired by Marvin Minsky's Society of Mind and MIT's FRL (Frame Representation Language). All source code is maintained in `SETUP.org` using literate programming and tangled to generate Python files.

## Development Commands

### Essential Commands
- **Run tests**: `python3 test_frames.py` or `make test`
- **Run examples interactively**: `python3 -i examples.py` or `make examples`
- **Tangle code from org**: `make tangle` (regenerates .py files from SETUP.org)
- **Cross-platform test**: `./test-all.sh` or `make test-all-platforms`

### Python Commands with UV
When using UV package manager, wrap all Python commands:
- `uv run pytest` (though tests use custom framework)
- `uv run python -m py_compile *.py` (verify imports)
- `uv run mypy *.py` (type checking)

### Docker Commands
- `make docker-build` - Build multi-platform image
- `make docker-test` - Run tests in container
- `make docker-run` - Interactive session

## Architecture

### Core Components

**Frame System (`frame_system.py`)**
- `Frame` class: Knowledge structures with slots and facets
- Global registry: `frames` dict maintains all frame instances
- FRL API: `fassert()`, `fget()`, `fput()`, `fdel()` for frame manipulation
- Facets: value, default, units, if_needed (lazy), if_added/if_removed (demons)

**Key Design Patterns**
1. **Lazy Evaluation**: `if_needed` facet computes values on demand with caching
2. **Active Values**: Demons (`if_added`, `if_removed`) trigger on value changes
3. **Prototype Inheritance**: Frames can inherit from other frames (`ako` slot)
4. **JSON Persistence**: `save_frames()`/`load_frames()` for state management

### File Organization
```
SETUP.org          # Master source file (literate programming)
frame_system.py    # Core frame implementation (tangled)
examples.py        # Usage demonstrations (tangled)
test_frames.py     # Test suite (tangled)
utils.py           # Visualization and helpers (tangled)
kitchen-ops.org    # Claude command definitions
```

## Development Workflow

1. **All code changes must be made in SETUP.org**, not in .py files
2. After editing SETUP.org, run `make tangle` to regenerate Python files
3. Test changes with `make test`
4. Use kitchen-themed Claude commands for specific tasks:
   - `/project:mise-en-place` - Initial setup
   - `/project:blanch` - Quick validation
   - `/project:reduce` - Optimize and refactor

## Frame System Usage

### Creating and Accessing Frames
```python
# Create frame with slots
fassert("person", {"name": "Alice", "age": 30})

# Access values
name = fget("person", "name")  # Returns "Alice"

# Update values
fput("person", "age", 31)

# Access with facets
fget("person", "age", "units")  # Returns None unless set
```

### Advanced Features
- **Computed Values**: Define `if_needed` procedures for lazy evaluation
- **Demons**: Add `if_added`/`if_removed` procedures for reactive behavior
- **Inheritance**: Use `ako` slot for prototype-based inheritance
- **Persistence**: Save/load entire frame system to/from JSON

## Testing

Tests use a custom `TestResults` class for reporting. The test suite covers:
- Basic frame operations
- Facet manipulation
- Computed values and caching
- Demon triggers
- Persistence round-trips
- Complex scenarios (smart home example)

Note: Tests currently have fixture issues with pytest but run correctly with `python3 test_frames.py`.

## Important Conventions

- No external dependencies - pure Python 3.6+ standard library only
- Cross-platform compatible (Linux, FreeBSD, macOS, Docker)
- All commits use conventional format with --trailer for co-authoring
- Frame names and slot names are strings
- Facet names are predefined: value, default, units, if_needed, if_added, if_removed, constraints