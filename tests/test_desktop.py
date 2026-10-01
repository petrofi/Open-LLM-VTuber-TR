"""Desktop regression tests: no network, microphone or LLM required."""
import base64
import importlib.util
import os
import tempfile
import unittest
import wave
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("desktop_server", ROOT / "scripts/desktop_server.py")
desktop = importlib.util.module_from_spec(spec)
spec.loader.exec_module(desktop)


class DesktopTests(unittest.TestCase):
    def test_user_data_survives_reseeding(self):
        with tempfile.TemporaryDirectory() as folder:
            data = Path(folder)
            desktop.prepare_user_data(data)
            (data / "conf.yaml").write_text("personal-config", "utf-8")
            (data / "chat_history/personal.json").write_text("[]", "utf-8")
            desktop.prepare_user_data(data)
            self.assertEqual((data / "conf.yaml").read_text("utf-8"), "personal-config")
            self.assertTrue((data / "chat_history/personal.json").is_file())

    def test_turkish_config_uses_real_schema(self):
        with tempfile.TemporaryDirectory() as folder:
            data = Path(folder)
            desktop.prepare_user_data(data)
            previous = Path.cwd()
            try:
                os.chdir(data)
                config = desktop.make_config({})
                self.assertEqual(config.system_config.host, "127.0.0.1")
                self.assertEqual(config.system_config.port, 0)
                self.assertEqual(config.character_config.asr_config.faster_whisper.language, "tr")
                self.assertEqual(config.character_config.tts_config.edge_tts.voice, "tr-TR-EmelNeural")
            finally:
                os.chdir(previous)

    def test_missing_model_does_not_download_at_startup(self):
        from src.open_llm_vtuber.asr.faster_whisper_asr import VoiceRecognition
        with tempfile.TemporaryDirectory() as folder, patch.dict(os.environ, {"OPEN_LLM_VTUBER_DESKTOP": "1"}):
            engine = VoiceRecognition(model_path=str(Path(folder) / "missing"), device="cpu", compute_type="int8", language="tr")
            self.assertIsNone(engine._model)
            with self.assertRaises(FileNotFoundError):
                engine._load_model()

    def test_wav_payload_preserves_audio(self):
        from src.open_llm_vtuber.utils.stream_audio import prepare_audio_payload
        import math
        import struct
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "tone.wav"
            with wave.open(str(source), "wb") as output:
                output.setparams((1, 2, 16000, 0, "NONE", "not compressed"))
                output.writeframes(b"".join(struct.pack("<h", int(1000 * math.sin(i * .2))) for i in range(16000)))
            payload = prepare_audio_payload(str(source))
            audio = base64.b64decode(payload["audio"])
            self.assertEqual(audio[:4], b"RIFF")
            self.assertGreater(len(audio), 1000)
            self.assertTrue(any(v > 0 for v in payload["volumes"]))


if __name__ == "__main__":
    unittest.main()
