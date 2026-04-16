"""
ZuesHammer Voice Module
"""

from .voice_system import (
    VoiceInteraction,
    LanguageDetector,
    WhisperSTT,
    EdgeTTS,
    VoiceConfig,
    Language,
)

from .wake_word import (
    VoiceManager,
    WakeWordDetector,
    VoiceMemory,
    VoiceProfile,
)

__all__ = [
    "VoiceInteraction",
    "LanguageDetector",
    "WhisperSTT",
    "EdgeTTS",
    "VoiceConfig",
    "Language",
    "VoiceManager",
    "WakeWordDetector",
    "VoiceMemory",
    "VoiceProfile",
]
