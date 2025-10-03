from enum import StrEnum


class OpenAIEvents(StrEnum):
    AUDIO_DELTA = "response.audio.delta"
    # ASSISTANT_TRANSCRIPT = "response.audio_transcript.delta"
    ASSISTANT_TRANSCRIPT = "response.audio_transcript.done"
    # CLIENT_TRANSCRIPT = "conversation.item.input_audio_transcription.delta"
    CLIENT_TRANSCRIPT = "conversation.item.input_audio_transcription.completed"
    SPEECH_STARTED = "input_audio_buffer.speech_started"
    TOOL_CALL = "response.function_call_arguments.done"


class EventType(StrEnum):
    MEDIA = "media"
    START = "start"
    MARK = "mark"
