from app.schemas.summary import MessageSchema


def format_transcript(transcript: list[MessageSchema]) -> str:
    formatted = []
    for msg in transcript:
        formatted.append(f"{msg.type}: {msg.content}")
    return "\n".join(formatted)