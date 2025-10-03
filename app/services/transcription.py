import re
from typing import AsyncGenerator
from uuid import UUID

from num2words import num2words

from app.core.mixins import LogMixin
from app.schemas.summary import Speaker
from app.services.summary import SummaryService


class TranscriptionService(LogMixin):
    def __init__(self, summary_service: SummaryService):
        self.sentence = ""
        self.message = []
        self.current_speaker = None

        self.summary_service = summary_service

    def save_message_to_summary(self, speaker: Speaker, sentence: str, session_id: UUID) -> None:
        if not self.current_speaker == speaker and self.current_speaker:
            self.summary_service.add_message(
                speaker=self.current_speaker,
                message=" ".join(self.message),
                session_id=session_id,
            )
            self.log(f"[AVA]: Saved message to memory of the speaker - {speaker}: {self.message}")
            self.current_speaker = speaker
            self.message.clear()

        self.message.append(sentence)

    async def proceed_llm_transcription(self, response: dict) -> AsyncGenerator[str]:
        transcript = response.get("delta", "").strip()
        if transcript:
            self.sentence += " " + transcript
            if transcript in "?!.":
                cleaned_sentence = self.clean_transcript(text=self.sentence)
                self.log(f"[AVA]: {Speaker.ASSISTANT} said: {cleaned_sentence}")
                yield cleaned_sentence
                self.sentence = ""

    async def proceed_transcription(self, response: dict, speaker: Speaker, session_id: UUID) -> None:
        transcript = response.get("transcript", "").strip()
        if not transcript:
            return None
        self.log(f"[AVA]: {speaker} said: {transcript}")
        self.summary_service.add_message(session_id=session_id, speaker=speaker, message=transcript)

    async def proceed_user_transcription(self, response: dict, session_id: UUID) -> None:
        transcript = response.get("transcript", "").strip()
        if not transcript:
            return None
        self.log(f"[AVA]: {Speaker.CLIENT} said: {transcript}")
        self.summary_service.add_message(session_id=session_id, speaker=Speaker.CLIENT, message=transcript)

    @staticmethod
    def replace_currency(match):
        amount = int(match.group(1).replace(",", ""))
        return num2words(amount, to="cardinal", lang="en") + " dollars"

    @staticmethod
    def replace_percent(match):
        number = match.group(1).replace(",", "")
        if "." in number:
            spoken = num2words(float(number), to="decimal", lang="en")
        else:
            spoken = num2words(int(number), to="cardinal", lang="en")
        return spoken + " percent"

    @staticmethod
    def replace_number(match):
        num = match.group(0)
        if len(num) > 2:
            return num2words(int(num), to="cardinal", lang="en")
        return num

    def clean_transcript(self, text: str) -> str:
        text = re.sub(r"(\$)\s*(\d+)\s*,\s*(\d+)", r"\1\2,\3", text)  # $ 1 , 650 → $1,650
        text = re.sub(r"(\$)\s*(\d+)", r"\1\2 ", text)  # $ 1650 → $1650
        text = re.sub(r"(\d)\s*,\s*(\d)", r"\1,\2", text)  # fix commas
        text = re.sub(r"(\d)\s*\.\s*(\d)", r"\1.\2", text)  # fix decimals
        text = re.sub(r"(\d)\s*%", r"\1%", text)  # fix percent
        text = re.sub(r"\$\s*([\d,]+)", self.replace_currency, text)
        text = re.sub(r"(\d+(?:\.\d+)?)\s*%", self.replace_percent, text)
        text = re.sub(r"\b\d{3,}\b", self.replace_number, text)
        text = re.sub(r"\s+([’,\-])", r"\1", text)
        text = re.sub(r"-\s+", "-", text)
        text = re.sub(r"\s+([.!?,:;])", r"\1", text)

        return text.strip()
