from __future__ import annotations

from typing import Dict

from orion.brain import create_model_provider
from orion.core.engine import RuntimeEngine
from orion.interface.cli import CLIInterface
from orion.interface.manager import InterfaceManager
from orion.utils.config import Config
from orion.utils.logger import get_logger
from orion.utils.system import OrionPaths
from orion.voice import (
    VoiceRuntime,
    VoiceService,
    WakeWordDetector,
    WakeWordProfile,
    create_windows_voice_service,
)


class OrionAssistant:
    """Top-level ORION application."""

    def __init__(self, config: Config) -> None:
        self.config = config
        self.paths = OrionPaths(config)
        self.logger = get_logger(
            "orion.core.assistant"
        )

        # -----------------------------------------------------
        # WAKE WORD
        # -----------------------------------------------------

        self.wake_word_profile = WakeWordProfile(
            user_id=config.get(
                "voice.wake_word.user_id",
                "local-user",
            ),
            phrase=config.get(
                "voice.wake_word.phrase",
                "hey orion",
            ),
            enabled=config.get(
                "voice.wake_word.enabled",
                True,
            ),
        )

        # -----------------------------------------------------
        # MODEL PROVIDER
        # -----------------------------------------------------

        model_provider = create_model_provider(
            provider_name=config.get(
                "brain.provider",
                "local",
            ),
            model_name=config.get(
                "brain.model",
                "",
            ),
            endpoint=config.get(
                "brain.endpoint",
                "http://127.0.0.1:11434/api/generate",
            ),
            timeout_seconds=float(
                config.get(
                    "brain.timeout_seconds",
                    120,
                )
            ),
        )

        # -----------------------------------------------------
        # RUNTIME ENGINE
        # -----------------------------------------------------

        self.engine = RuntimeEngine(
            wake_word_detector=WakeWordDetector(
                self.wake_word_profile
            ),
            model_provider=model_provider,
        )

        # -----------------------------------------------------
        # VOICE SERVICE
        # -----------------------------------------------------

        self.voice_service: VoiceService | None = None

        self.voice_runtime: VoiceRuntime | None = None

        if config.get(
            "voice.enabled",
            False,
        ):
            self.voice_service = (
                create_windows_voice_service(
                    event_bus=self.engine.event_bus,
                    model_path=config.get(
                        "voice.microphone.vosk_model_path",
                        "",
                    ),
                    sample_rate=int(
                        config.get(
                            "voice.microphone.sample_rate",
                            16000,
                        )
                    ),
                    default_capture_seconds=float(
                        config.get(
                            "voice.microphone.duration_seconds",
                            5,
                        )
                    ),
                    auto_speak_responses=config.get(
                        "voice.auto_speak_responses",
                        True,
                    ),
                )
            )

            self.voice_runtime = VoiceRuntime(
                service=self.voice_service,
                event_bus=self.engine.event_bus,
                capture_interval_seconds=float(
                    config.get(
                        "voice.runtime.capture_interval_seconds",
                        0.0,
                    )
                ),
                error_retry_delay_seconds=float(
                    config.get(
                        "voice.runtime.error_retry_delay_seconds",
                        2.0,
                    )
                ),
                join_timeout_seconds=float(
                    config.get(
                        "voice.runtime.join_timeout_seconds",
                        3.0,
                    )
                ),
            )

        # -----------------------------------------------------
        # INTERFACES
        # -----------------------------------------------------

        self.interfaces = InterfaceManager()

        self.cli = CLIInterface(
            self.engine.event_bus
        )

        self.interfaces.register(
            self.cli
        )

        self.initialized = False

    # =========================================================
    # INITIALIZATION
    # =========================================================

    def initialize(self) -> None:
        """Initialize ORION foundation and runtime."""

        if self.initialized:
            self.logger.warning(
                "ORION initialization requested more than once."
            )
            return

        self.logger.info(
            "Starting ORION initialization."
        )

        self.paths.create_directories()

        self.engine.initialize()

        self.initialized = True

        self.logger.info(
            "ORION initialization completed."
        )

    # =========================================================
    # START
    # =========================================================

    def start(self) -> None:
        """Start ORION."""

        if not self.initialized:
            self.initialize()

        self.logger.info(
            "Starting ORION."
        )

        self.engine.start()

        self.interfaces.start_all()

        if self.voice_runtime is not None:
            self.voice_runtime.start()

        self.logger.info(
            "ORION is now running."
        )

    # =========================================================
    # RUN
    # =========================================================

    def run(self) -> None:
        """Run ORION."""

        if not self.initialized:
            self.initialize()

        if not self.engine.is_running:
            self.start()

        self.engine.run(
            self.cli
        )

    # =========================================================
    # STOP
    # =========================================================

    def stop(self) -> None:
        """Stop ORION runtime components."""

        self.logger.info(
            "Stopping ORION."
        )

        if self.voice_runtime is not None:
            self.voice_runtime.stop()

        self.engine.stop()

    # =========================================================
    # SHUTDOWN
    # =========================================================

    def shutdown(self) -> None:
        """Shutdown ORION completely."""

        self.logger.info(
            "Shutting down ORION."
        )

        # Stop background voice processing first.
        if self.voice_runtime is not None:
            self.voice_runtime.stop()

        elif self.voice_service is not None:
            self.voice_service.stop()

        # Stop interfaces.
        self.interfaces.stop_all()

        # Shutdown core engine.
        self.engine.shutdown()

        self.initialized = False

        self.logger.info(
            "ORION shutdown completed."
        )

    # =========================================================
    # STATUS
    # =========================================================

    def status(self) -> Dict[str, object]:
        """Return current ORION status."""

        status: Dict[str, object] = {
            "configuration": (
                self.config is not None
            ),
            "paths": self.paths.data.exists(),
            "initialized": self.initialized,
            "runtime_state": (
                self.engine.state.value
            ),
            "running": self.engine.is_running,
            "voice_enabled": (
                self.voice_service is not None
            ),
            "voice_runtime_running": (
                self.voice_runtime.is_running
                if self.voice_runtime is not None
                else False
            ),
        }

        self.logger.debug(
            "ORION status: %s",
            status,
        )

        return status