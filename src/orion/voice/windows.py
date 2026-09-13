from __future__ import annotations

import base64
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable, Optional

from orion.voice.contracts import (
    AudioCapture,
    AudioChunk,
    AudioFormat,
    SpeechRecognizer,
    SpeechSynthesizer,
    VoiceError,
    VoiceTranscript,
)


class SoundDeviceMicrophoneCapture(AudioCapture):
    """Optional local microphone adapter powered by sounddevice."""

    def __init__(
        self,
        audio_format: AudioFormat = AudioFormat(),
        device: Optional[int | str] = None,
    ) -> None:
        self.audio_format = audio_format
        self.device = device

    def capture(
        self,
        duration_seconds: float,
    ) -> AudioChunk:
        """Capture one bounded PCM microphone segment."""

        if duration_seconds <= 0:
            raise ValueError(
                "Capture duration must be positive."
            )

        frame_count = int(
            duration_seconds
            * self.audio_format.sample_rate
        )

        if frame_count <= 0:
            raise ValueError(
                "Capture duration is too short for the configured sample rate."
            )

        try:
            import sounddevice as sd  # type: ignore
        except ImportError as exc:
            raise VoiceError(
                "Microphone support requires the optional voice dependencies."
            ) from exc

        try:
            recording = sd.rec(
                frame_count,
                samplerate=self.audio_format.sample_rate,
                channels=self.audio_format.channels,
                dtype="int16",
                device=self.device,
            )

            sd.wait()

        except Exception as exc:
            raise VoiceError(
                "Unable to capture microphone audio. "
                "Check microphone permissions, device availability, "
                "and Windows audio settings."
            ) from exc

        try:
            data = recording.tobytes()
        except Exception as exc:
            raise VoiceError(
                "Microphone returned an invalid audio buffer."
            ) from exc

        if not data:
            raise VoiceError(
                "Microphone returned an empty audio buffer."
            )

        return AudioChunk(
            data=data,
            format=self.audio_format,
        )


class VoskSpeechRecognizer(SpeechRecognizer):
    """Optional offline speech recognizer powered by a local Vosk model."""

    def __init__(self, model_path: Path) -> None:
        self.model_path = Path(model_path)

    def transcribe(self, audio: AudioChunk) -> VoiceTranscript:
        if audio.format.channels != 1 or audio.format.sample_width_bytes != 2:
            raise VoiceError(
                "Vosk recognition requires mono 16-bit PCM audio."
            )

        try:
            from vosk import KaldiRecognizer, Model  # type: ignore
        except ImportError as exc:
            raise VoiceError(
                "Speech recognition requires the optional voice dependencies."
            ) from exc

        try:
            model = Model(str(self.model_path))
            recognizer = KaldiRecognizer(
                model,
                audio.format.sample_rate,
            )
            recognizer.AcceptWaveform(audio.data)
            payload = json.loads(recognizer.FinalResult())
        except Exception as exc:
            raise VoiceError("Unable to transcribe microphone audio.") from exc

        text = payload.get("text", "")

        if not isinstance(text, str):
            raise VoiceError("Speech recognizer returned invalid transcript text.")

        return VoiceTranscript(text=text)


ProcessRunner = Callable[..., Any]


class WindowsSpeechSynthesizer(SpeechSynthesizer):
    """Windows offline TTS adapter using the built-in System.Speech API."""

    def __init__(
        self,
        runner: ProcessRunner = subprocess.run,
    ) -> None:
        self._runner = runner

    def speak(self, text: str) -> None:
        if not text.strip():
            return

        if sys.platform != "win32":
            raise VoiceError(
                "Windows speech synthesis is only available on Windows."
            )

        encoded_text = base64.b64encode(
            text.encode("utf-16le")
        ).decode("ascii")
        script = (
            "Add-Type -AssemblyName System.Speech; "
            "$voice = New-Object "
            "System.Speech.Synthesis.SpeechSynthesizer; "
            "$text = [Text.Encoding]::Unicode.GetString("
            f"[Convert]::FromBase64String('{encoded_text}')); "
            "$voice.Speak($text)"
        )

        try:
            self._runner(
                [
                    "powershell",
                    "-NoProfile",
                    "-NonInteractive",
                    "-Command",
                    script,
                ],
                check=True,
                timeout=60,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            raise VoiceError("Unable to synthesize speech on Windows.") from exc
