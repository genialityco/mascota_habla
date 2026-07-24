from typing import Protocol


class TTSService(Protocol):
    def synthesize(self, text: str, sexo: str | None = None) -> bytes: ...
