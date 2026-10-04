import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from src.open_llm_vtuber.asr.model_download import download_model


class Response:
    def __init__(self, data):
        self.data = data

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def raise_for_status(self):
        pass

    def iter_content(self, size):
        yield self.data


class ModelDownloadTests(unittest.TestCase):
    def manifest(self, data):
        return {"repo": "Systran/faster-whisper-small", "revision": "pinned",
                "files": [{"name": "model.bin", "size": len(data),
                           "sha256": hashlib.sha256(data).hexdigest()}]}

    def test_verified_download_is_atomic_and_reused(self):
        data = b"verified test model"
        with tempfile.TemporaryDirectory() as directory:
            with patch("src.open_llm_vtuber.asr.model_download.requests.get", return_value=Response(data)) as get:
                download_model(directory, self.manifest(data))
                get.assert_called_once()
            with patch("src.open_llm_vtuber.asr.model_download.requests.get") as get:
                download_model(directory, self.manifest(data))
                get.assert_not_called()
            self.assertEqual((Path(directory) / "model.bin").read_bytes(), data)
            self.assertFalse((Path(directory) / "model.bin.partial").exists())

    def test_bad_hash_does_not_replace_existing_file(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "model.bin"
            target.write_bytes(b"existing model")
            with patch("src.open_llm_vtuber.asr.model_download.requests.get", return_value=Response(b"bad")):
                with self.assertRaises(ValueError):
                    download_model(directory, self.manifest(b"yes"))
            self.assertEqual(target.read_bytes(), b"existing model")
            self.assertFalse(target.with_name("model.bin.partial").exists())

    def test_manifest_cannot_escape_model_folder(self):
        manifest = self.manifest(b"test")
        manifest["files"][0]["name"] = "../model.bin"
        with tempfile.TemporaryDirectory() as directory, self.assertRaises(ValueError):
            download_model(directory, manifest)
