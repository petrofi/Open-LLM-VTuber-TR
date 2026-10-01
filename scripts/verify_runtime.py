"""Real desktop startup, speech and shutdown verification (no credentials logged)."""
import argparse
import base64
import json
import os
import subprocess
import sys
import time
from pathlib import Path
import httpx

ROOT = Path(__file__).resolve().parents[1]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--speech", action="store_true")
    args = parser.parse_args()
    data = ROOT / ".build/qa-data"
    data.mkdir(parents=True, exist_ok=True)
    token = os.urandom(32).hex()
    report = {}
    err = (data / "process-error.log").open("w", encoding="utf-8")
    child = subprocess.Popen([sys.executable, str(ROOT / "scripts/desktop_server.py"), "--data-dir", str(data)],
        cwd=ROOT, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=err, text=True, encoding="utf-8",
        env={**os.environ, "PYTHONUTF8": "1"})
    try:
        child.stdin.write(json.dumps({"token": token, "settings": {}}) + "\n")
        child.stdin.flush()
        # Timeout is enforced by the outer verification runner as well.
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as pool:
            line = pool.submit(child.stdout.readline).result(timeout=120)
        if not line:
            raise RuntimeError("Backend closed before port announcement")
        port = json.loads(line)["port"]
        client = httpx.Client(base_url=f"http://127.0.0.1:{port}", headers={"x-tr-token": token}, timeout=60, trust_env=False)
        deadline = time.monotonic() + 120
        while True:
            if child.poll() is not None:
                raise RuntimeError("Backend exited before readiness")
            try:
                result = client.get("/tr/health")
                if result.is_success:
                    break
            except httpx.HTTPError:
                pass
            if time.monotonic() > deadline:
                raise TimeoutError("Backend readiness")
            time.sleep(.25)
        report["startup"] = result.json()
        report["unauthenticated_status"] = httpx.get(f"http://127.0.0.1:{port}/tr/health").status_code
        report["providers"] = client.get("/tr/providers").json()
        if args.speech:
            result = client.post("/tr/tts/test")
            result.raise_for_status()
            sample = data / "turkce-ses.mp3"
            sample.write_bytes(result.content)
            report["tts_bytes"] = sample.stat().st_size
            sys.path.insert(0, str(ROOT))
            from src.open_llm_vtuber.utils.stream_audio import prepare_audio_payload
            payload = prepare_audio_payload(str(sample))
            wav = data / "turkce-ses.wav"
            wav.write_bytes(base64.b64decode(payload["audio"]))
            report["frontend_audio_payload"] = {"bytes": wav.stat().st_size, "volume_frames": len(payload["volumes"])}
            result = client.post("/tr/asr/download")
            result.raise_for_status()
            deadline = time.monotonic() + 1200
            while time.monotonic() < deadline:
                state = client.get("/tr/asr/status").json()
                if state["state"] == "error":
                    raise RuntimeError(state["message"])
                if state["state"] == "ready":
                    break
                time.sleep(2)
            else:
                raise TimeoutError("ASR download")
            # Upstream /asr expects 16 kHz PCM WAV; decode and resample explicitly.
            from faster_whisper.audio import decode_audio
            import numpy as np
            import wave
            import asyncio
            import edge_tts
            sentence = "Merhaba, bu bir Türkçe konuşma tanıma testidir."
            fixture_mp3 = data / "turkce-fixture.mp3"
            asyncio.run(edge_tts.Communicate(sentence, "tr-TR-EmelNeural").save(str(fixture_mp3)))
            report["asr_expected"] = sentence
            audio = decode_audio(str(fixture_mp3), sampling_rate=16000)
            fixture = data / "turkce-asr.wav"
            with wave.open(str(fixture), "wb") as output:
                output.setparams((1, 2, 16000, 0, "NONE", "not compressed"))
                output.writeframes((np.clip(audio, -1, 1) * 32767).astype(np.int16).tobytes())
            with fixture.open("rb") as f:
                result = client.post("/asr", files={"file": ("test.wav", f, "audio/wav")}, timeout=180)
            result.raise_for_status()
            report["asr"] = result.json()
            text = report["asr"]["text"].lower()
            if not all(word in text for word in ("merhaba", "türkçe", "konuşma", "tanıma")):
                raise AssertionError("Turkish ASR fixture not recognized meaningfully")
        print(json.dumps(report, ensure_ascii=False, indent=2), flush=True)
        (ROOT / ".build/runtime-verification.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    finally:
        child.stdin.close()
        try:
            child.wait(timeout=15)
        except subprocess.TimeoutExpired:
            child.kill()
            child.wait()
            raise RuntimeError("Backend shutdown exceeded 15 seconds")
        err.close()
        print("shutdown_exit_code=" + str(child.returncode), flush=True)

if __name__ == "__main__":
    main()
