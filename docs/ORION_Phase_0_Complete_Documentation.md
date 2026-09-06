# ORION — Phase 0 Documentation
## Architecture & Foundation

**Project:** O.R.I.O.N. — Operational Reasoning Intelligent Orchestration Network  
**Distribution:** `orion-assistant`  
**Python package:** `orion`  
**Phase:** 0 — Architecture & Foundation  
**Platform baseline:** Windows  
**Python baseline:** `>=3.10,<3.14`  

---

## 1. Phase 0 Overview

Phase 0 establishes the technical foundation for ORION.

The goal is to create a modular, local-first, provider-independent architecture that later phases can extend without requiring major structural changes.

### Phase 0 objectives

- Establish the repository and package structure.
- Define configuration management.
- Establish logging and observability.
- Build the core runtime lifecycle.
- Create an event-driven communication layer.
- Abstract user interfaces.
- Define tool and memory contracts.
- Establish a security foundation.
- Build automated tests and validate the foundation.

### Milestones

| Milestone | Component | Status |
|---|---|---|
| 0A | Repository & Project Structure | Complete |
| 0B | Configuration Management | Complete |
| 0C | Logging & Observability | Complete |
| 0D | Core Runtime | Complete |
| 0E | Event System | Complete |
| 0F | Interface Abstraction | Complete |
| 0G | Tool & Memory Interfaces | Complete |
| 0H | Security Foundation | Complete |
| 0I | Testing & Phase-0 Validation | Final validation |

---

## 2. Design Principles

### 2.1 Local-first

ORION is designed to operate locally whenever practical. Online services should be providers rather than hard-coded dependencies.

### 2.2 Modular

Subsystems are separated into independent packages:

- `core`
- `brain`
- `interface`
- `tools`
- `memory`
- `security`
- `online`
- `utils`

### 2.3 Provider-independent

Subsystems use abstractions so implementations can change without requiring changes to the core.

Examples:

```text
BaseTool
   └── future tool implementations

BaseMemory
   └── future memory implementations
```

### 2.4 Event-driven

Subsystem communication is designed around the `EventBus`, reducing direct coupling.

### 2.5 Security-first

System-level operations will eventually pass through permission and confirmation checks.

### 2.6 Testable

Components are designed so they can be tested independently using mock implementations.

---

## 3. Repository Structure

```text
ORION/
├── .github/workflows/tests.yml
├── config/
│   ├── config.yaml
│   ├── logging.yaml
│   └── environments/
│       ├── development.yaml
│       └── production.yaml
├── data/
│   ├── cache/.gitkeep
│   ├── knowledge/.gitkeep
│   └── memory/.gitkeep
├── docs/
│   ├── architecture.md
│   ├── development.md
│   └── phase-0.md
├── logs/.gitkeep
├── models/.gitkeep
├── scripts/setup.py
├── src/orion/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── assistant.py
│   │   ├── engine.py
│   │   ├── events.py
│   │   └── state.py
│   ├── brain/
│   │   ├── __init__.py
│   │   ├── intent.py
│   │   ├── planner.py
│   │   └── reasoning.py
│   ├── interface/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── cli.py
│   │   ├── manager.py
│   │   ├── output.py
│   │   └── voice.py
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── registry.py
│   ├── memory/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── manager.py
│   ├── security/
│   │   ├── __init__.py
│   │   ├── permissions.py
│   │   └── validator.py
│   ├── online/__init__.py
│   └── utils/
│       ├── __init__.py
│       ├── config.py
│       ├── logger.py
│       └── system.py
├── tests/
│   ├── __init__.py
│   ├── test_config.py
│   ├── test_events.py
│   ├── test_interface.py
│   ├── test_logging.py
│   ├── test_memory.py
│   ├── test_runtime.py
│   ├── test_security.py
│   ├── test_structure.py
│   └── test_tools.py
├── .env.example
├── .gitignore
├── LICENSE
├── README.md
├── main.py
├── pyproject.toml
└── requirements.txt
```

---

# 4. 0A — Repository & Project Structure

## Objective

Create a clean Python project layout suitable for long-term development.

The distribution name is:

```text
orion-assistant
```

The import package is:

```python
import orion
```

The project uses a `src` layout:

```text
src/
└── orion/
```

The supported Python baseline is:

```text
Python >=3.10,<3.14
```

The project uses setuptools through `pyproject.toml`.

Runtime dependencies include:

- `python-dotenv`
- `PyYAML`

Development dependencies include:

- `pytest`
- `pytest-cov`

---

# 5. 0B — Configuration Management

## Objective

Centralize configuration and separate environment-specific settings from application code.

Configuration flow:

```text
.env
  │
  ▼
config/config.yaml
  │
  ▼
config/environments/<environment>.yaml
  │
  ▼
merged configuration
```

The default environment is:

```text
development
```

Selected through:

```env
ORION_ENV=development
```

Important base configuration:

```yaml
orion:
  name: ORION
  version: "0.1.0"

runtime:
  debug: false
  data_directory: data
  log_directory: logs
  model_directory: models

interface:
  default: cli

brain:
  provider: local
  model: ""

memory:
  enabled: true

security:
  enabled: true
  require_confirmation: true
```

The configuration loader:

1. Loads `.env`.
2. Loads base YAML.
3. Loads environment-specific YAML.
4. Deep-merges the configurations.
5. Applies supported environment variables.
6. Validates required keys.
7. Provides `get()` and `require()` access.

---

# 6. 0C — Logging & Observability

## Objective

Provide consistent logging throughout ORION.

The system uses Python's standard `logging` package and `logging.config.dictConfig`.

Log outputs:

```text
Console
logs/
├── orion.log
└── errors.log
```

Supported levels:

```text
DEBUG
INFO
WARNING
ERROR
CRITICAL
```

File logs use rotating handlers to prevent unlimited growth.

Components obtain loggers through:

```python
from orion.utils.logger import get_logger

logger = get_logger("component.name")
```

---

# 7. 0D — Core Runtime

## Objective

Create the lifecycle controller for ORION.

The runtime is represented by `RuntimeEngine`.

### Runtime states

```text
CREATED
   │
   ▼
INITIALIZING
   │
   ▼
RUNNING
   │
   ▼
STOPPING
   │
   ▼
STOPPED
```

An additional `FAILED` state is defined for error conditions.

### Runtime responsibilities

- initialization
- startup
- interface execution
- stopping
- shutdown
- runtime state management
- EventBus ownership

The runtime exposes:

```python
engine.state
engine.is_running
engine.event_bus
```

Interfaces are executed through:

```python
engine.run(interface)
```

which delegates to:

```python
engine.run_interface(interface)
```

The CLI runtime supports:

```text
exit
quit
shutdown
```

and handles `KeyboardInterrupt` and `EOFError`.

---

# 8. 0E — Event System

## Objective

Create a central communication mechanism between ORION components.

### Event

An `Event` contains:

```text
type
payload
event_id
timestamp
source
```

Event IDs are UUID-based and timestamps use UTC.

### Event types

```text
STARTUP
SHUTDOWN
USER_INPUT
SYSTEM_EVENT
ERROR
TOOL_REQUEST
MEMORY_REQUEST
VOICE_INPUT
WAKE_WORD
```

### EventBus

The EventBus provides:

```text
subscribe()
unsubscribe()
publish()
clear()
subscriber_count()
```

Example:

```text
CLI
 │
 │ USER_INPUT
 ▼
EventBus
 │
 ├── Brain
 ├── Logging
 └── future subscribers
```

---

# 9. 0F — Interface Abstraction

## Objective

Allow multiple interaction mechanisms without changing the core runtime.

### BaseInterface

Every interface follows the common contract:

```text
BaseInterface
├── name
├── event_bus
├── is_running
├── start()
├── stop()
├── receive()
├── send()
├── publish_input()
└── publish_shutdown()
```

### CLIInterface

The CLI provides terminal interaction and publishes user input through the EventBus.

### VoiceInterface

A voice interface abstraction exists for future speech recognition and synthesis. Actual voice implementation is deferred to the Voice phase.

### InterfaceManager

The manager provides:

```text
register()
unregister()
get()
start()
stop()
start_all()
stop_all()
names()
count()
```

Duplicate interface registration is prevented.

---

# 10. 0G — Tool & Memory Interfaces

## Objective

Define provider-independent contracts for tools and memory.

Actual powerful tools and persistent memory providers are deferred to later phases.

## 10.1 Tool abstraction

`BaseTool` defines:

```text
name
description
metadata()
execute()
```

Tools receive:

```text
parameters
context
```

`ToolContext` currently provides the source of a request, for example:

```python
ToolContext(source="cli")
```

`ToolRegistry` manages:

```text
register()
unregister()
get()
has()
names()
count()
clear()
```

Duplicate tool registration is rejected.

## 10.2 Memory abstraction

`BaseMemory` defines:

```text
store()
retrieve()
search()
delete()
clear()
```

`MemoryRecord` contains:

```text
content
memory_id
metadata
timestamp
```

`MemoryManager` provides:

```text
store()
retrieve()
search()
delete()
clear()
```

The memory manager is independent of the underlying storage provider.

---

# 11. 0H — Security Foundation

## Objective

Establish security boundaries before ORION receives powerful system-control capabilities.

### Permission hierarchy

```text
NONE
  ↓
READ
  ↓
WRITE
  ↓
EXECUTE
  ↓
ADMIN
```

### PermissionManager

Determines whether granted permission satisfies required permission.

Example:

```text
Granted READ, Required READ   → allowed
Granted READ, Required WRITE  → denied
```

### SecurityRequest

Contains:

```text
action
permission
parameters
```

### SecurityValidator

Validates security requests and raises `SecurityError` when permission is insufficient.

### ConfirmationManager

Confirmation is separate from permission.

Current confirmation policy:

```text
READ       → no confirmation
WRITE      → confirmation
EXECUTE    → confirmation
ADMIN      → confirmation
```

The confirmation mechanism is deliberately not coupled to `input()` or the CLI. Future interfaces can provide the actual user approval mechanism.

Security flow:

```text
Tool Request
     │
     ▼
SecurityValidator
     │
     ├── denied ──► SecurityError
     │
     ▼
Permission allowed
     │
     ▼
ConfirmationManager
     │
     ├── not required ──► continue
     │
     └── required ──────► user approval
```

---

# 12. 0I — Testing & Phase-0 Validation

## Objective

Validate the complete Phase 0 foundation.

Tests are organized by subsystem:

```text
tests/
├── test_config.py
├── test_events.py
├── test_interface.py
├── test_logging.py
├── test_memory.py
├── test_runtime.py
├── test_security.py
├── test_structure.py
└── test_tools.py
```

Testing includes:

- unit tests
- mock implementations
- integration tests
- structural tests
- configuration validation
- runtime lifecycle validation
- event validation
- interface validation
- tool validation
- memory validation
- security validation

The project test suite reached a reported baseline of **54 passing tests** during Phase 0 development. The exact count may increase as final validation tests are added.

The acceptance criterion is:

```text
0 failures
0 errors
```

Warnings should also be resolved where practical.

---

# 13. Validation Commands

### Complete test suite

```powershell
pytest -v
```

### Compact output

```powershell
pytest -q
```

### Individual test groups

```powershell
pytest tests/test_config.py -v
pytest tests/test_events.py -v
pytest tests/test_interface.py -v
pytest tests/test_logging.py -v
pytest tests/test_memory.py -v
pytest tests/test_runtime.py -v
pytest tests/test_security.py -v
pytest tests/test_structure.py -v
pytest tests/test_tools.py -v
```

### Syntax validation

```powershell
python -m compileall src
```

### Package validation

```powershell
python -c "import orion; print('ORION import OK')"
```

### Assistant validation

```powershell
python -c "from orion.core.assistant import OrionAssistant; print('Assistant import OK')"
```

---

# 14. Complete Phase-0 Architecture

```text
                         ORION
                           │
                    ┌──────▼──────┐
                    │ Orion       │
                    │ Assistant   │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │ Runtime     │
                    │ Engine      │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │ EventBus    │
                    └──────┬──────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
   Interfaces           Tools              Memory
        │                  │                  │
 BaseInterface        BaseTool           BaseMemory
        │                  │                  │
 CLI / Voice          Registry            Manager
        │
        └──────────────────┬──────────────────┐
                           │                  │
                           ▼                  ▼
                       Security          Future Brain
                           │
                 Permission + Confirmation
```

---

# 15. Dependency Direction

The intended dependency direction is:

```text
Interfaces
    │
    ▼
Core / Event System
    │
    ├── Tools
    ├── Memory
    └── Security
```

Future intelligence layers should consume these abstractions rather than bypass them.

Circular dependencies between major subsystems should be avoided.

---

# 16. What Phase 0 Does Not Implement

Phase 0 intentionally does not implement:

- LLM reasoning
- intent classification
- advanced planning
- wake-word detection
- speech recognition
- text-to-speech
- browser automation
- OS automation
- application control
- persistent vector memory
- online search
- autonomous agents
- computer vision
- proactive behavior

These belong to later phases.

Phase 0 provides the infrastructure required by those features.

---

# 17. Phase 1 Readiness

After Phase 0 validation, the next major layer is:

```text
Phase 1 — Core Brain
```

The future flow is:

```text
User
 │
 ▼
Interface
 │
 ▼
EventBus
 │
 ▼
Core Runtime
 │
 ▼
Brain
 ├── Intent
 ├── Reasoning
 └── Planning
 │
 ▼
Tool / Memory / Security abstractions
 │
 ▼
Response
```

The brain should use the established abstractions rather than directly controlling the operating system or hard-coding providers.

---

# 18. Phase 0 Definition of Done

Phase 0 is complete when:

1. The repository structure exists.
2. ORION can load configuration.
3. ORION can initialize required directories.
4. ORION can initialize and start its runtime.
5. ORION can communicate through the EventBus.
6. Interfaces are abstracted from the runtime.
7. Tools have a standard execution contract.
8. Memory has a standard provider contract.
9. Sensitive operations have a security boundary.
10. Confirmation requirements are defined.
11. Automated tests validate the foundation.
12. The complete test suite passes without failures.
13. No Phase-0 component requires a specific future LLM, database, or online provider.

---

# 19. Phase 0 Summary

Phase 0 transforms ORION from an empty project into a structured software foundation.

The foundation now consists of:

```text
Configuration
     │
Logging
     │
Runtime
     │
Events
     │
Interfaces
     │
Tools
     │
Memory
     │
Security
     │
Testing
     │
     ▼
Phase 1 — Core Brain
```

The architecture is intentionally designed so that future intelligence, voice, wake-word, system-control, memory, online, vision, personality, and autonomous capabilities can be added without replacing the foundation.

---

## Phase 0 Status

**Architecture & Foundation: COMPLETE**

**Next:** Phase 1 — Core Brain
