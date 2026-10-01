import os
import threading
from pathlib import Path
import numpy as np
from faster_whisper import WhisperModel
from .asr_interface import ASRInterface


class VoiceRecognition(ASRInterface):
    BEAM_SEARCH = True
    # SAMPLE_RATE # Defined in asr_interface.py

    def __init__(
        self,
        model_path: str = "distil-medium.en",
        download_root: str = None,
        language: str = "en",
        device: str = "auto",
        compute_type: str = "int8",
        prompt: str = None,
    ) -> None:
        self.MODEL_PATH = model_path
        self.LANG = language
        self.prompt = prompt
        self._model_options = dict(
            model_size_or_path=model_path, download_root=download_root,
            device=device, compute_type=compute_type,
        )
        self._model = None
        self._model_lock = threading.Lock()
        if os.environ.get("OPEN_LLM_VTUBER_DESKTOP") != "1":
            self._load_model()

    def _load_model(self):
        with self._model_lock:
            if self._model is None:
                if os.environ.get("OPEN_LLM_VTUBER_DESKTOP") == "1":
                    if not (Path(self.MODEL_PATH) / "model.bin").is_file():
                        raise FileNotFoundError(
                            "Türkçe konuşma modeli henüz indirilmemiş. İlk kurulum ekranından indirin."
                        )
                    self._model_options["local_files_only"] = True
                self._model = WhisperModel(**self._model_options)
        return self._model

    @property
    def model(self):
        return self._load_model()

    def transcribe_np(self, audio: np.ndarray) -> str:
        if self.prompt:
            segments, info = self.model.transcribe(
                audio,
                beam_size=5 if self.BEAM_SEARCH else 1,
                language=self.LANG if self.LANG else None,
                condition_on_previous_text=False,
                initial_prompt=self.prompt,
            )
        else:
            segments, info = self.model.transcribe(
                audio,
                beam_size=5 if self.BEAM_SEARCH else 1,
                language=self.LANG if self.LANG else None,
                condition_on_previous_text=False,
            )
        text = [segment.text for segment in segments]

        if not text:
            return ""
        else:
            return "".join(text)
