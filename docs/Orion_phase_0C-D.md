# ORION — Phase 0C & Phase 0D Documentation

**Project:** O.R.I.O.N. — Operational Reasoning Intelligent Orchestration Network  
**Version:** 0.1.0  
**Python:** >=3.10,<3.14  
**Initial Platform:** Windows

---

## 1. Overview

Phase 0 establishes the foundation of ORION before higher-level AI capabilities are introduced.

This document covers:

- **Phase 0C — Logging & Observability**
- **Phase 0D — Core Runtime**

These phases make ORION capable of initializing its infrastructure, producing structured logs, recording errors, maintaining a controlled lifecycle, running continuously, accepting shutdown commands, and shutting down cleanly.

AI reasoning, voice, wake word, tools, memory, vision, and online intelligence are intentionally deferred to later phases.

---

# Phase 0C — Logging & Observability

## 2. Objective

Phase 0C introduces a centralized logging system based on Python's standard `logging` framework.

The architecture is:

```text
                    ORION LOGGER
                         |
             +-----------+-----------+
             |           |           |
             v           v           v
          Console    orion.log   errors.log
           INFO+       DEBUG+       ERROR+
```

## 3. Logging Requirements

Implemented capabilities:

- Centralized logging configuration
- Console logging
- Persistent file logging
- Dedicated error logging
- Rotating log files
- Configurable log level
- Component-specific loggers
- Exception logging
- Runtime log-directory creation
- Logging tests

## 4. Logging Configuration

Configuration file:

```text
config/logging.yaml
```

Logging policy:

| Level | Console | `orion.log` | `errors.log` |
|---|---:|---:|---:|
| DEBUG | No | Yes | No |
| INFO | Yes | Yes | No |
| WARNING | Yes | Yes | No |
| ERROR | Yes | Yes | Yes |
| CRITICAL | Yes | Yes | Yes |

The ORION logger can run at DEBUG while the console remains at INFO. This keeps the terminal readable while retaining detailed diagnostics in the log file.

## 5. Logger Hierarchy

ORION uses the `orion` namespace:

```text
orion
├── core
│   ├── startup
│   ├── assistant
│   └── engine
├── brain
├── tools
├── security
└── memory
```

Examples:

```python
get_logger("orion.core.engine")
get_logger("orion.brain.reasoning")
get_logger("orion.tools.registry")
```

## 6. Log Files

Runtime output:

```text
logs/
├── orion.log
└── errors.log
```

`orion.log` contains detailed ORION activity.

`errors.log` contains ERROR/CRITICAL messages and exception tracebacks.

## 7. Log Rotation

Both file handlers use rotating logs.

Current policy:

```text
Maximum size: 5 MB
Backups:      5
```

Example:

```text
orion.log
orion.log.1
orion.log.2
orion.log.3
orion.log.4
orion.log.5
```

## 8. Log Format

The standard format is:

```text
YYYY-MM-DD HH:MM:SS | LEVEL | LOGGER | MESSAGE
```

Example:

```text
2026-09-04 13:00:00 | INFO | orion.core.startup | ORION startup sequence initiated.
```

## 9. Logging Level Configuration

Development:

```env
ORION_LOG_LEVEL=DEBUG
```

Production:

```env
ORION_LOG_LEVEL=INFO
```

The distinction is:

```text
Logger level   → controls messages entering the pipeline
Handler level  → controls where messages are written
```

## 10. Logging API

Implementation:

```text
src/orion/utils/logger.py
```

Main functions:

```python
setup_logging(...)
get_logger(...)
log_exception(...)
```

### `setup_logging()`

Loads the YAML logging configuration, creates the log directory, redirects file handlers to the runtime log directory, validates the requested level, and initializes Python logging.

### `get_logger()`

Creates or retrieves an ORION component logger.

### `log_exception()`

Convenience wrapper for exception logging.

## 11. Exception Logging

Use:

```python
try:
    risky_operation()
except Exception:
    logger.exception("Operation failed.")
```

This records the message and traceback.

## 12. Security Considerations

Do not casually log:

- API keys
- Passwords
- Access tokens
- Private keys
- Authentication headers
- Sensitive personal information
- Private memory contents

Future security components should add explicit redaction where necessary.

## 13. Phase 0C Tests

Tests are located at:

```text
tests/test_logging.py
```

They verify:

- Logging initialization
- Log file creation
- Logger namespaces
- Namespace normalization
- Exception logging
- Traceback contents

## 14. Phase 0C Architecture

```text
main.py
   |
   v
Config
   |
   v
OrionPaths
   |
   v
setup_logging()
   |
   v
ORION Logger
   |
   +----> Console
   |
   +----> logs/orion.log
   |
   +----> logs/errors.log
```

---

# Phase 0D — Core Runtime

## 15. Objective

Phase 0D converts the foundation into a real application runtime.

Lifecycle:

```text
CREATED
   |
   v
INITIALIZING
   |
   v
RUNNING
   |
   v
STOPPING
   |
   v
STOPPED
```

A `FAILED` state is also defined for future explicit failure handling.

## 16. Runtime State

Implementation:

```text
src/orion/core/state.py
```

States:

```python
CREATED
INITIALIZING
RUNNING
STOPPING
STOPPED
FAILED
```

### State meanings

- **CREATED** — Runtime object exists but is not initialized.
- **INITIALIZING** — Runtime components are being prepared.
- **RUNNING** — Runtime is active.
- **STOPPING** — Shutdown is in progress.
- **STOPPED** — Shutdown completed.
- **FAILED** — Reserved for runtime failure handling.

## 17. Runtime Engine

Implementation:

```text
src/orion/core/engine.py
```

The engine provides:

```python
initialize()
start()
run()
stop()
shutdown()
```

and exposes:

```python
state
is_running
```

The engine is intentionally independent of the future brain, tools, memory, voice, and interfaces.

## 18. Runtime Initialization

```text
RuntimeEngine created
        |
        v
initialize()
        |
        v
INITIALIZING
        |
        v
Runtime ready
```

Initialization clears the shutdown event and prepares the runtime for execution.

## 19. Runtime Start

`start()` transitions:

```text
INITIALIZING → RUNNING
```

When running:

```python
engine.is_running
```

returns:

```text
True
```

## 20. Runtime Loop

The current runtime loop is deliberately simple.

It accepts terminal input:

```text
ORION >
```

For example:

```text
ORION > hello
ORION received: hello
```

At this stage ORION does not interpret commands with an AI model. The input loop is a temporary runtime mechanism.

Future architecture:

```text
CLI / Voice / Wake Word
          |
          v
      Event System
          |
          v
     Runtime Engine
          |
          v
         Brain
```

## 21. Shutdown

The preferred shutdown commands are:

```text
exit
quit
shutdown
```

Example:

```text
ORION > exit
```

Lifecycle:

```text
RUNNING
   |
   v
STOPPING
   |
   v
STOPPED
```

`Ctrl+C` remains available as a fallback through `KeyboardInterrupt`.

## 22. Stop Event

The runtime uses:

```python
threading.Event
```

as the shutdown signal.

Conceptually:

```text
Runtime loop
     |
     v
Wait for shutdown
     |
     v
Shutdown requested
     |
     v
STOPPING
     |
     v
STOPPED
```

This avoids a CPU-intensive busy loop and prepares ORION for future event-driven and asynchronous functionality.

## 23. OrionAssistant

Implementation:

```text
src/orion/core/assistant.py
```

`OrionAssistant` connects configuration, filesystem paths, logging, and the runtime engine.

It exposes:

```python
initialize()
start()
run()
stop()
shutdown()
status()
```

## 24. Application Lifecycle

```text
main.py
   |
   v
Config
   |
   v
OrionPaths
   |
   v
Logging
   |
   v
OrionAssistant
   |
   v
initialize()
   |
   v
start()
   |
   v
run()
   |
   v
exit / quit / shutdown
   |
   v
stop()
   |
   v
shutdown()
```

## 25. Runtime Status

`OrionAssistant.status()` reports:

```text
configuration
paths
initialized
runtime_state
running
```

Example:

```python
{
    "configuration": True,
    "paths": True,
    "initialized": True,
    "runtime_state": "running",
    "running": True,
}
```

## 26. Main Entry Point

Implementation:

```text
main.py
```

Startup sequence:

1. Determine project root
2. Load configuration
3. Create runtime directories
4. Initialize logging
5. Create `OrionAssistant`
6. Initialize assistant
7. Start runtime
8. Enter runtime loop
9. Handle shutdown
10. Cleanup

`main.py` coordinates startup; it should not contain future AI reasoning logic.

## 27. Error Handling

The runtime uses structured exception handling:

```python
try:
    ...
except KeyboardInterrupt:
    ...
except Exception:
    logger.exception(...)
finally:
    assistant.shutdown()
```

The `finally` block ensures cleanup is attempted even after unexpected failures.

## 28. Phase 0D Tests

Tests are located at:

```text
tests/test_runtime.py
```

They verify:

- Initial state is `CREATED`
- Initialization transitions to `INITIALIZING`
- Start transitions to `RUNNING`
- Stop transitions to `STOPPED`
- Shutdown leaves the runtime stopped
- `OrionAssistant` correctly controls the runtime

## 29. Manual Runtime Validation

Run:

```powershell
python main.py
```

Expected:

```text
ORION is running.
Type 'exit' to shut down.

ORION >
```

Then enter:

```text
exit
```

Expected behavior includes:

```text
Shutdown command received: exit
Stopping ORION runtime.
ORION runtime stopped.
ORION runtime loop exited.
ORION shutdown completed.
```

## 30. Test Suite

Run:

```powershell
pytest -v
```

Relevant tests:

```text
tests/
├── test_config.py
├── test_logging.py
├── test_runtime.py
└── test_structure.py
```

All tests should pass before Phase 0D is considered complete.

---

# 31. Phase 0C Checklist

- [x] Central logging configuration
- [x] Console logging
- [x] Main ORION log
- [x] Error log
- [x] Rotating logs
- [x] Configurable logging level
- [x] Component-specific loggers
- [x] Exception logging
- [x] Runtime log-directory creation
- [x] Logging tests
- [x] Startup logging integration

# 32. Phase 0D Checklist

- [x] Runtime state model
- [x] Runtime engine
- [x] Initialization lifecycle
- [x] Start lifecycle
- [x] Running state
- [x] Runtime loop
- [x] Shutdown signal
- [x] `exit` command
- [x] `quit` command
- [x] `shutdown` command
- [x] Ctrl+C fallback
- [x] Graceful shutdown
- [x] Runtime exception handling
- [x] Assistant/runtime integration
- [x] Runtime tests

---

# 33. Current Architecture

```text
                         ORION
                           |
                           v
                        main.py
                           |
                           v
                   OrionAssistant
                           |
              +------------+------------+
              |                         |
              v                         v
        Configuration            RuntimeEngine
              |                         |
              v                         v
         OrionPaths                RuntimeState
              |                         |
              v                         v
          Filesystem                Runtime Loop
              |
              v
           Logging
              |
       +------+------+ 
       |      |      |
       v      v      v
    Console  Log   Errors
```

---

# 34. Next Phase — 0E Event System

The current runtime accepts raw terminal input:

```text
ORION > command
```

Phase 0E will introduce a proper internal event architecture:

```text
CLI / Voice / System / Wake Word
             |
             v
        Event Producer
             |
             v
          Event Bus
             |
             v
       Runtime Engine
             |
             v
        Event Handler
```

Potential events:

```text
USER_INPUT
SYSTEM_EVENT
STARTUP
SHUTDOWN
ERROR
TOOL_REQUEST
MEMORY_REQUEST
VOICE_INPUT
WAKE_WORD
```

This event layer will decouple ORION's future interfaces and subsystems.

---

# 35. Engineering Principle

The central architectural principle established in 0C and 0D is:

> **The runtime should orchestrate components, not contain their intelligence.**

Responsibilities remain separated:

```text
main.py
    → application startup

OrionAssistant
    → application coordination

RuntimeEngine
    → lifecycle and execution

Event System
    → communication

Brain
    → reasoning

Tools
    → actions

Memory
    → persistent context

Interface
    → user interaction
```

This separation is the foundation for extending ORION through Phases 1–10.

---

# 36. Phase 0 Progress

```text
Phase 0
│
├── 0A Repository & Project Structure     COMPLETE
├── 0B Configuration Management           COMPLETE*
├── 0C Logging & Observability            COMPLETE
├── 0D Core Runtime                       COMPLETE
├── 0E Event System                       NEXT
├── 0F Interface Abstraction              PENDING
├── 0G Tool & Memory Interfaces            PENDING
├── 0H Security Foundation                PENDING
└── 0I Testing & Phase-0 Validation       PENDING
```

`*` Before final Phase-0 validation, verify that the development configuration correctly produces:

```text
runtime.debug = true
```

when:

```text
ORION_ENV=development
```

and:

```text
ORION_LOG_LEVEL=DEBUG
```

---

