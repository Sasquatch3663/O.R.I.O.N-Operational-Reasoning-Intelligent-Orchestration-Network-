ORION --- Phase 0 Documentation

Architecture, Repository Foundation & Configuration System

Project: ORION --- Operational Reasoning Intelligent Orchestration
Network
Current Version: 0.1.0
Current Phase: Phase 0 --- Architecture & Foundation
Completed Milestones: Phase 0A + Phase 0B implementation
Python Baseline: 3.10+
Initial Platform: Windows
Architecture: Local-first, modular, extensible

1. Project Overview

ORION is a personal AI system assistant designed to become a
local-first, system-integrated assistant capable of:

Natural-language interaction

Voice interaction

System and application control

Long-term and short-term memory

Reasoning and task planning

Optional online intelligence

Vision and screen understanding

Controlled automation

Personalized behavior

The project is being developed incrementally. Phase 0 establishes the
software architecture and development foundation before intelligence or
automation features are introduced.

The central design principle is:

Build a stable, modular foundation first; add intelligence and
capabilities as independent components later.

2. Development Roadmap

The overall ORION roadmap is:

Phase                   Area                    Objective

0                       Architecture &          Establish project
Foundation              architecture and
infrastructure

1                       Core Brain              Reasoning, intent
recognition and
responses

2                       Voice                   Speech-to-text and
text-to-speech

3                       Wake Word               Wake-word detection and
activation

4                       Tool System             Computer and system
control

5                       Memory                  Short-term and
long-term memory

6                       Online Intelligence     Web search, APIs and
external services

7                       Planning & Agents       Multi-step task
execution

8                       Vision                  Screen/image/camera
understanding

9                       Personality &           Personalized and
Proactivity             proactive behavior

Only Phase 0 is currently being implemented.

3. Phase 0 Objectives

Phase 0 is divided into:

0A --- Repository & Project Structure

0B --- Configuration Management

0C --- Logging & Observability

0D --- Core Runtime

0E --- Event System

0F --- Interface Abstraction

0G --- Tool & Memory Interfaces

0H --- Security Foundation

0I --- Testing & Phase-0 Validation

Current work covers 0A and 0B.

4. Technology Baseline

Python

ORION uses:

Python >= 3.10 and < 3.14

Python 3.10 was selected as the minimum supported version to maintain
compatibility with the project's intended AI, automation and
system-integration ecosystem while still allowing modern Python
features.

The project configuration specifies:

requires-python = ">=3.10,<3.14"

Current Dependencies

Runtime

python-dotenv
PyYAML

Development

pytest
pytest-cov

Additional dependencies will be introduced only when required by later
phases.

5. Repository Architecture

The current target repository structure is:

ORION/
│
├── .github/
│   └── workflows/
│       └── tests.yml
│
├── config/
│   ├── config.yaml
│   ├── logging.yaml
│   └── environments/
│       ├── development.yaml
│       └── production.yaml
│
├── data/
│   ├── cache/
│   │   └── .gitkeep
│   ├── knowledge/
│   │   └── .gitkeep
│   └── memory/
│       └── .gitkeep
│
├── docs/
│   ├── architecture.md
│   └── development.md
│
├── logs/
│   └── .gitkeep
│
├── models/
│   └── .gitkeep
│
├── scripts/
│   └── setup.py
│
├── src/
│   └── orion/
│       │
│       ├── __init__.py
│       │
│       ├── core/
│       │   ├── __init__.py
│       │   ├── assistant.py
│       │   ├── engine.py
│       │   ├── events.py
│       │   └── state.py
│       │
│       ├── brain/
│       │   ├── __init__.py
│       │   ├── intent.py
│       │   ├── planner.py
│       │   └── reasoning.py
│       │
│       ├── interface/
│       │   ├── __init__.py
│       │   ├── cli.py
│       │   ├── output.py
│       │   └── voice.py
│       │
│       ├── tools/
│       │   ├── __init__.py
│       │   ├── base.py
│       │   └── registry.py
│       │
│       ├── memory/
│       │   ├── __init__.py
│       │   ├── base.py
│       │   └── manager.py
│       │
│       ├── security/
│       │   ├── __init__.py
│       │   ├── permissions.py
│       │   └── validator.py
│       │
│       ├── online/
│       │   └── __init__.py
│       │
│       └── utils/
│           ├── __init__.py
│           ├── config.py
│           ├── logger.py
│           └── system.py
│
├── tests/
│   ├── __init__.py
│   ├── test_config.py
│   └── test_structure.py
│
├── .env.example
├── .gitignore
├── LICENSE
├── README.md
├── main.py
├── pyproject.toml
└── requirements.txt

Some directories and modules are intentionally placeholders for later
phases.

6. Architectural Responsibilities

src/orion/core

The application orchestration layer.

Future responsibilities include:

Assistant lifecycle

Runtime state

Event handling

Component coordination

Main execution flow

src/orion/brain

The intelligence layer.

Future responsibilities include:

Intent recognition

Reasoning

Planning

LLM integration

Response generation

No actual reasoning engine has been implemented yet.

src/orion/interface

The user interaction layer.

Planned interfaces include:

CLI

Voice

Output rendering

Future GUI/API interfaces

Voice functionality belongs to Phase 2.

src/orion/tools

The controlled action layer.

Future tools may include:

Application control

Filesystem operations

Browser operations

System operations

Media control

Developer tools

Automation

The LLM/core should interact with tools through defined interfaces
rather than directly executing arbitrary system commands.

src/orion/memory

The memory subsystem.

Planned capabilities:

Working/short-term memory

Long-term memory

Knowledge storage

Retrieval

Memory management

Actual memory implementation is scheduled for Phase 5.

src/orion/security

The security and permission boundary.

The intended execution architecture is:

User Request
     ↓
ORION Brain
     ↓
Tool Request
     ↓
Validation
     ↓
Permission Check
     ↓
Execution

This prevents the reasoning system from becoming an unrestricted
execution layer.

src/orion/online

Reserved for optional online functionality such as:

Web search

APIs

External services

Online information retrieval

The local-first principle means online functionality should remain
optional.

src/orion/utils

Shared infrastructure.

Current utilities include:

Configuration management

Filesystem/path management

Logging support

7. Phase 0A --- Repository Foundation

Phase 0A established:

Git repository

Python package

src/ layout

Runtime directories

Test directory

Documentation directory

Configuration directory

Project metadata

Environment template

Git ignore rules

Setup script

The src/ layout separates the package source from repository-level
files.

This allows the project to eventually be installed as a normal Python
package.

8. Python Packaging

The project is defined using pyproject.toml.

Important metadata:

name = "orion-assistant"
version = "0.1.0"
description = "ORION - Local-first personal AI system assistant"
requires-python = ">=3.10,<3.14"
license = { text = "MIT" }

The Python distribution name and Python import package are different
concepts:

Distribution:
orion-assistant

Python package:
orion

Therefore imports use:

from orion.utils.config import Config

9. Phase 0B --- Configuration Management

The configuration subsystem provides one central configuration interface
for ORION.

The main implementation is:

src/orion/utils/config.py

The configuration system supports:

YAML configuration

Environment-specific configuration

.env

Environment variables

Nested configuration access

Configuration merging

Required-value validation

10. Configuration Hierarchy

Configuration sources are processed in this order:

config/config.yaml
        ↓
environment-specific YAML
        ↓
.env
        ↓
system environment variables
        ↓
final ORION configuration

Later/higher-priority values override earlier values.

For example:

# config.yaml

runtime:
  debug: false

can be overridden by:

# environments/development.yaml

runtime:
  debug: true

An environment variable can then override a supported value again.

11. Base Configuration

The base configuration is:

orion:
  name: ORION
  version: "0.1.0"

environment:
  default: development

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

This provides defaults shared across environments.

12. Development Configuration

Development configuration:

runtime:
  debug: true

logging:
  level: DEBUG

security:
  require_confirmation: true

It is intended to override the base configuration when:

ORION_ENV=development

13. Production Configuration

Production configuration:

runtime:
  debug: false

logging:
  level: INFO

security:
  require_confirmation: true

This provides safer defaults for a production deployment.

14. Environment File

The project contains:

.env.example

The local .env file is intentionally excluded from Git.

Example:

ORION_ENV=development

ORION_NAME=ORION
ORION_VERSION=0.1.0

ORION_LOG_LEVEL=DEBUG

ORION_MODEL_PROVIDER=local
ORION_MODEL_NAME=

OPENAI_API_KEY=

The .env file is loaded through python-dotenv.

The actual .env file must never be committed because future versions
may contain secrets such as API keys.

15. Configuration Manager

The Config class is responsible for:

Locating the project root

Loading .env

Loading base YAML

Determining the active environment

Loading environment-specific YAML

Deep-merging configuration

Applying supported environment variables

Validating required settings

Example:

from orion.utils.config import Config

config = Config()

name = config.get("orion.name")

Nested values can be accessed using dot notation:

config.get("runtime.data_directory")

Required values can be retrieved with:

config.require("orion.name")

16. Configuration Validation

The following values are currently required:

orion.name
orion.version
runtime.data_directory
runtime.log_directory
runtime.model_directory
interface.default
brain.provider
memory.enabled
security.enabled

If a required configuration value is missing, ConfigurationError is
raised.

This prevents ORION from silently starting with an invalid
configuration.

17. Filesystem Path Management

The project contains:

src/orion/utils/system.py

which defines OrionPaths.

Instead of constructing paths throughout the application, ORION
centralizes them.

Examples:

paths.data
paths.memory
paths.knowledge
paths.cache
paths.logs
paths.models

The resulting structure is:

data/
├── memory/
├── knowledge/
└── cache/

logs/

models/

The path manager can create the runtime directories automatically.

18. Current ORION Initialization Flow

The current entry point is:

main.py

The initialization flow is:

main.py
   │
   ▼
Determine project root
   │
   ▼
Create Config
   │
   ├── Load .env
   ├── Load config.yaml
   ├── Select environment
   ├── Load environment YAML
   ├── Merge configuration
   ├── Apply environment variables
   └── Validate
   │
   ▼
Create OrionAssistant
   │
   ▼
Create OrionPaths
   │
   ▼
Create runtime directories
   │
   ▼
ORION initialized

19. Current Assistant Foundation

OrionAssistant currently provides:

assistant.initialize()
assistant.status()

At this stage it does not perform AI reasoning.

Its purpose is to establish the application boundary that future
components will plug into.

20. Logging Configuration

A logging configuration file has been prepared:

config/logging.yaml

Current format:

timestamp | level | logger | message

Example:

2026-09-02 14:30:00 | INFO | orion.assistant | Initializing ORION...

Full logging implementation is part of:

Phase 0C --- Logging & Observability.

21. Testing

The project currently contains tests for:

Configuration loading

Environment selection

Nested configuration access

Path management

Repository structure

Required project files

Tests are executed using:

pytest

The goal is to ensure the foundation remains stable as additional ORION
components are introduced.

22. Installation

Create the virtual environment with Python 3.10:

py -3.10 -m venv .venv

Activate it:

.venv\Scripts\Activate.ps1

Verify:

python --version

Expected:

Python 3.10.x

Install ORION in editable mode:

pip install -e ".[dev]"

Editable installation allows source changes to be reflected immediately
without reinstalling the package after every modification.

23. Running ORION

From the repository root:

python main.py

The current foundation should report:

============================================================
                         ORION
             Personal AI System Assistant
============================================================

System
-------
Name:        ORION
Version:     0.1.0
Environment: development

Foundation
----------
Configuration : READY
Filesystem    : READY
Runtime       : READY

ORION foundation initialized successfully.
============================================================

24. Configuration Verification

The current configuration can be inspected using:

python -c "from orion.utils.config import Config; c=Config(); print(c.data)"

The current observed configuration is:

{
    'orion': {
        'name': 'ORION',
        'version': '0.1.0'
    },
    'environment': 'development',
    'runtime': {
        'debug': False,
        'data_directory': 'data',
        'log_directory': 'logs',
        'model_directory': 'models'
    },
    'interface': {
        'default': 'cli'
    },
    'brain': {
        'provider': 'local',
        'model': ''
    },
    'memory': {
        'enabled': True
    },
    'security': {
        'enabled': True,
        'require_confirmation': True
    },
    'logging': {
        'level': 'DEBUG'
    }
}

25. Current Configuration Issue

The current output confirms that:

ORION_ENV=development

is being detected.

It also confirms:

logging.level = DEBUG

is being loaded.

However:

runtime.debug = False

is currently still coming from the base configuration rather than the
expected development override.

Expected development value:

runtime.debug = True

The development configuration file should contain:

runtime:
  debug: true

logging:
  level: DEBUG

security:
  require_confirmation: true

This issue should be resolved before formally closing Phase 0B.

26. Security of Configuration

The project follows these rules:

.env is not committed.

API keys should never be placed in YAML configuration.

Secrets should be supplied through environment variables or a future
secret-management mechanism.

Configuration validation should fail early when required settings
are missing.

Configuration should not contain personal memory data.

27. Git Workflow

After completing a stable milestone:

git status

Then:

git add .

Commit:

git commit -m "Initialize ORION Phase 0 foundation"

Future milestones should receive separate commits, for example:

Phase 0A — Repository foundation
Phase 0B — Configuration system
Phase 0C — Logging system
Phase 0D — Core runtime

This keeps the project's development history understandable.

28. Design Principles Established

The following architectural principles are now established for ORION.

Local-first

Core functionality should not depend on an internet connection whenever
practical.

Modular

Each major capability has its own subsystem.

Provider-independent

The reasoning layer should not be permanently tied to one AI provider.

Security-first

Computer-control operations should pass through validation and
permissions.

Observable

Important ORION operations should be traceable through logs.

Configuration-driven

Runtime behavior should be controlled through configuration rather than
hard-coded values.

Extensible

Future features should be added as components rather than rewriting the
core.

29. Phase 0A + 0B Completion Checklist

Phase 0A

Git repository initialized

Python project created

Python 3.10 baseline established

src/ package layout created

Core directories created

Data directories created

Tests directory created

Documentation directory created

.gitignore created

.env.example created

pyproject.toml created

requirements.txt created

Initial README created

Setup script created

Phase 0B

Base YAML configuration

Development configuration

Production configuration

.env loading

Environment selection

Configuration merging

Environment variable overrides

Nested configuration access

Required configuration validation

Centralized filesystem paths

Resolve runtime.debug development override

Final 0B validation

30. Next Phase

After the remaining Phase 0B configuration issue is resolved,
development continues with:

Phase 0C --- Logging & Observability

Objectives:

Logging
   ↓
Structured application logs
   ↓
Component-specific loggers
   ↓
File + console handlers
   ↓
Log rotation
   ↓
Error reporting
   ↓
Runtime diagnostics

After 0C:

0D — Core Runtime
0E — Event System
0F — Interface Abstraction
0G — Tool & Memory Interfaces
0H — Security Foundation
0I — Testing & Phase-0 Validation

Only after Phase 0 is complete should ORION move to:

Phase 1 --- Core Brain

31. Phase 0 Success Criteria

Phase 0 will ultimately be considered complete when:

ORION starts cleanly
        ↓
Configuration loads correctly
        ↓
Logging is operational
        ↓
Core runtime initializes
        ↓
Events can be dispatched
        ↓
Interfaces can communicate with Core
        ↓
Tools have defined boundaries
        ↓
Memory has defined boundaries
        ↓
Security layer is active
        ↓
Automated tests pass

At that point, ORION will have a reliable software foundation on which
the actual AI system can be built.

Document status: Living documentation
Last documented milestone: Phase 0A + 0B
Next milestone: Phase 0C --- Logging & Observability