# Development Principles

Core principles that apply to ALL coding in this project.

---

## Core Philosophy

- **Functional minimalism**: Implement the minimum complexity necessary for current requirements
- **Incrementality**: Test each change before proceeding, implement one component at a time
- **Privacy-first**: All data processing happens locally, no external cloud services
- **Effective simplicity**: Prefer the simplest solution that works
- **Reversibility**: Return to working versions when optimizations compromise functionality

## Critical Approach

- Critically evaluate and question questionable assumptions
- For ambiguous questions: identify the unclear part and ask for direct clarification
- Do not develop elaborate explanations for possible interpretations of the question

---

## Development Workflow

When developing code or debugging, always follow these general rules:

1. **Development**: Work on one bug, feature, or thematically coherent development at a time
2. **Verify**: Run linting (ruff) and type checking (mypy) to verify correctness
3. **User Testing**: Let the user test the changes from her perspective
4. **Atomic Commit**: Create a single, focused commit for the completed work

This cycle ensures:

- **Focus**: One logical change per iteration
- **Quality**: Immediate verification through lint and type check
- **Traceability**: Clean commit history with atomic, reversible changes
- **Reliability**: Each commit represents a working state

---

## Technology Compatibility

- Verify complete compatibility between proposed frameworks and libraries
- Explicitly list compatibility requirements before suggesting any library
- Confirm active support for third-party libraries with recent framework versions
- Compare alternatives highlighting compatibility advantages/disadvantages
- Report potential integration problems before implementation

---

## State and Lifecycle Management

- Clearly define the possible states of each component
- Document allowable state transitions
- Properly manage resource cleanup (database sessions, async connections)
- Implement appropriate state management patterns
- Avoid inconsistent states or race conditions

---

## Async and Concurrency

- Use async/await consistently in FastAPI endpoints and services
- Manage database sessions with proper lifecycle (context managers)
- Handle httpx client connections responsibly
- Consider timeout strategies for external service calls (Ollama)
