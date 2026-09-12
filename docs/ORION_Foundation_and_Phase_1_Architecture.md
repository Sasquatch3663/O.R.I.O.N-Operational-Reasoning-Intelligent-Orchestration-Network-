# ORION — Foundation and Phase 1 Architecture

**Project:** O.R.I.O.N. — Operational Reasoning Intelligent Orchestration Network  
**Distribution:** `orion-assistant`  
**Python package:** `orion`  
**Python baseline:** `>=3.10,<3.14`  
**Current status:** Phase 0 and Phase 1 complete  
**Validated test suite:** 79 passing tests

---

## 1. Product Direction

ORION is a local-first companion intended for two clients that share one core:

- A lightweight Windows desktop pet/overlay.
- An Android companion application.

The intended avatar is a friendly, rounded white robot with a dark display face, mint/cyan illumination, and soft purple accents. The core does not contain a UI toolkit or image asset. Instead, it emits platform-neutral avatar state and gesture requests which each client renders in its own way.

Each user owns a configurable wake phrase. The phrase is a user preference, not a hard-coded application command.

---

## 2. Architecture Principles

| Principle | Decision |
|---|---|
| Local-first | Providers are optional and replaceable; deterministic reasoning remains available without a model. |
| Cross-platform | Windows and Android UI, audio, and packaging remain outside the core Python domain layer. |
| Event-driven | Interfaces, wake-word adapters, the brain, and avatar UIs communicate through `EventBus` events. |
| Security-first | Plans state required permissions and confirmation requirements before execution. |
| Testable | Contracts use plain Python models and can be tested without a microphone, LLM, or GUI. |

---

## 3. Repository Structure

```text
src/orion/
├── brain/
│   ├── engine.py          # Brain orchestration and event integration
│   ├── input.py           # Normalized user input
│   ├── intent.py          # Rule-based intent analysis
│   ├── model.py           # Provider-neutral model contracts
│   ├── planner.py         # Security-aware plans
│   └── reasoning.py       # Deterministic reasoning
├── core/
│   ├── assistant.py       # Top-level application assembly
│   ├── engine.py          # Runtime lifecycle and wake-word routing
│   ├── events.py          # Event and EventBus contracts
│   └── state.py
├── interface/             # CLI and future client interfaces
├── memory/                # Provider-independent memory contracts
├── pet/
│   └── behavior.py        # Avatar states and gesture selection
├── security/              # Permissions and confirmation policies
├── tools/                 # Provider-independent tool contracts
├── voice/
│   └── wake_word.py       # User wake-profile and text-level matching
└── utils/                 # Configuration, logging, and paths
```

---

## 4. Phase 0 — Foundation (Complete)

Phase 0 established the stable system boundaries that Phase 1 builds on.

| Milestone | Capability | Status |
|---|---|---|
| 0A | Repository and `src` package layout | Complete |
| 0B | YAML, `.env`, and environment configuration | Complete |
| 0C | Console and rotating-file logging | Complete |
| 0D | Runtime lifecycle and state management | Complete |
| 0E | Synchronous `EventBus` | Complete |
| 0F | Abstract interface and CLI contracts | Complete |
| 0G | Tool and memory provider contracts | Complete |
| 0H | Permission and confirmation contracts | Complete |
| 0I | Automated validation | Complete |

### Foundation contracts

```text
BaseInterface  → user/client boundary
BaseTool       → executable capability boundary
BaseMemory     → memory-provider boundary
EventBus       → component communication boundary
SecurityValidator + ConfirmationManager → execution safety boundary
```

### Permission hierarchy

```text
NONE → READ → WRITE → EXECUTE → ADMIN
```

`WRITE`, `EXECUTE`, and `ADMIN` operations require confirmation according to the current default policy.

---

## 5. Phase 1 — Core Brain (Completed Work)

The Phase 1 goal is a structured, provider-independent intelligence pipeline that understands input and produces plans without requiring an LLM.

```text
UserInput
    │
    ▼
IntentAnalyzer
    │
    ▼
ReasoningEngine
    │
    ▼
Planner
    │
    ▼
BrainResult
```

### 5.1 Input normalization

`UserInput` trims text, preserves its source, and rejects empty input.

### 5.2 Intent analysis

The initial rule-based analyzer supports:

```text
UNKNOWN
QUESTION
CONVERSATION
TOOL_REQUEST
MEMORY_REQUEST
```

Examples:

```text
"What is Python?"            → QUESTION
"remember that ORION is local" → MEMORY_REQUEST
"open calculator"            → TOOL_REQUEST
```

### 5.3 Deterministic reasoning and planning

`ReasoningEngine` produces a response, actions, and confidence. `Planner` turns actions into `PlanStep` objects.

| Planned action | Required permission | Confirmation |
|---|---:|---|
| `memory_store` | `WRITE` | Yes |
| `tool_request` | `EXECUTE` | Yes |
| Other/default | `READ` | No |

`BrainEngine.validate_plan()` invokes a configured `SecurityValidator`; actual tool or memory execution remains a future execution-layer responsibility.

### 5.4 Brain and EventBus

The runtime owns the `EventBus`. `BrainEngine` subscribes to `USER_INPUT`, processes it, and publishes `BRAIN_RESPONSE`.

```text
CLI / future client
       │ USER_INPUT
       ▼
    EventBus
       │
       ▼
  BrainEngine
       │
       ├── BRAIN_RESPONSE
       └── AVATAR_EXPRESSION
```

The response payload contains the response text, actions, confidence, plan, model metadata when present, memory count, and the selected avatar expression.

### 5.5 Memory and tool context

Optional `MemoryManager` and `ToolRegistry` dependencies enrich `ReasoningContext` with relevant memories and available tool names. The brain does not bypass their contracts or execute unapproved actions.

### 5.6 Model-provider abstraction and local adapter

`BaseModelProvider` defines one provider-neutral operation:

```python
generate(request: ModelRequest) -> ModelResponse
```

`ModelRequest` carries normalized text, intent, relevant memories, and available tool names. A configured provider may improve the user-facing response; deterministic planning remains the authority for actions. With no provider configured, ORION continues using its deterministic response path.

Phase 1K adds `OllamaModelProvider`, a dependency-free adapter for a local Ollama service. It sends a non-streaming request to the configured local `/api/generate` endpoint and converts the returned text into `ModelResponse`. Configure a local model name to enable it:

```yaml
brain:
  provider: local
  model: "qwen2.5:3b"
  endpoint: "http://127.0.0.1:11434/api/generate"
  timeout_seconds: 120
```

Leaving `brain.model` blank keeps deterministic mode active. If a configured local service cannot be reached, the brain preserves the deterministic response and records model availability metadata in `BRAIN_RESPONSE`; it does not permit the model failure to disrupt planning.

### 5.7 Phase 1 validation

Phase 1 is complete because the following boundaries are exercised by automated tests:

```text
Wake phrase + spoken command
    → WAKE_WORD
    → USER_INPUT
    → BrainResult / security-aware Plan
    → BRAIN_RESPONSE + AVATAR_EXPRESSION
```

Validation also confirms that a disabled wake profile does not activate, malformed user-input events are rejected, a local-model failure falls back safely to deterministic reasoning, and a model-enhanced response cannot alter deterministic plan permissions.

---

## 6. Wake Phrase Foundation

The `voice` package currently implements configuration and transcript matching, not microphone capture or acoustic wake-word recognition.

```text
VOICE_INPUT transcript
        │
        ▼
WakeWordDetector
        │ match
        ▼
WAKE_WORD event
```

`WakeWordProfile` contains:

```text
user_id
phrase
enabled
```

The default profile is configured in `config/config.yaml`:

```yaml
voice:
  wake_word:
    enabled: true
    user_id: local-user
    phrase: "hey orion"
```

Platform-specific Windows and Android audio adapters will publish `VOICE_INPUT` events after speech recognition or dedicated wake-word detection. This keeps microphone permissions, battery policy, and OS-specific services out of the core.

---

## 7. Companion-Pet Expression System

The `pet` package defines a UI-independent contract for the avatar.

### States

```text
IDLE
LISTENING
THINKING
HAPPY
ALERT
```

### Gestures

```text
IDLE_BOB
WAVE
NOD
HEAD_TILT
FOCUS
CELEBRATE
```

`AvatarBehavior` maps brain outcomes to `AvatarExpression` events. Current examples:

| Trigger | State | Gesture |
|---|---|---|
| Wake phrase detected | `LISTENING` | `HEAD_TILT` |
| Question | `THINKING` | `HEAD_TILT` |
| Memory request | `HAPPY` | `NOD` |
| Tool request | `THINKING` | `FOCUS` |
| Confident conversation | `HAPPY` | `WAVE` |

The Windows overlay and Android app will subscribe to `AVATAR_EXPRESSION` and animate the reference character appropriately. This decoupling allows distinct renderers—2D, sprite, Rive, Lottie, or 3D—without changing core reasoning.

---

## 8. Current Event Types

```text
STARTUP
SHUTDOWN
USER_INPUT
BRAIN_RESPONSE
AVATAR_EXPRESSION
VOICE_INPUT
WAKE_WORD
SYSTEM_EVENT
ERROR
TOOL_REQUEST
MEMORY_REQUEST
```

---

## 9. Configuration

Relevant current configuration:

```yaml
brain:
  provider: local
  model: ""
  endpoint: "http://127.0.0.1:11434/api/generate"
  timeout_seconds: 120

voice:
  wake_word:
    enabled: true
    user_id: local-user
    phrase: "hey orion"

avatar:
  style: "cute-white-robot"
  accent_color: "mint-cyan"

security:
  enabled: true
  require_confirmation: true
```

Configuration can be overridden through the existing configuration system. A future user-profile layer should persist each user’s wake phrase and avatar preferences securely.

---

## 10. Validation

Run the complete suite from the project root:

```powershell
pytest -q
```

Current result:

```text
79 passed
```

Coverage includes configuration, runtime lifecycle, events, interfaces, tools, memory, security, deterministic brain processing, provider injection, avatar expressions, model fallback, malformed-event handling, and the complete wake phrase → brain → pet event path.

---

## 11. Explicitly Deferred Work

The present codebase deliberately does not yet implement:

- A packaged Windows desktop overlay or Android application.
- Microphone capture, acoustic wake-word models, speech-to-text, or text-to-speech.
- Per-user account/profile storage and cross-device synchronization.
- Actual tool execution or persistent memory implementation.
- Avatar assets, rigging, rendering, or animation playback.

These are separate implementation phases. The contracts introduced so far keep them from requiring a rewrite of the core brain.

---

## 12. Next Recommended Milestones

1. **Voice phase:** Select platform audio adapters and connect them to `VOICE_INPUT`.
2. **Pet UI phase:** Build Windows and Android renderers that subscribe to `AVATAR_EXPRESSION`.
3. **Execution phase:** Add approved tool/memory executors behind existing security checks.

## Status

**Phase 0 — Architecture & Foundation: COMPLETE**  
**Phase 1 — Core Brain: COMPLETE**
