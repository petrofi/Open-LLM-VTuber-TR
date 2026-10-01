"""Packaged desktop entry point. No global Python, Git or interactive console."""
import argparse
import asyncio
import json
import os
import secrets
import shutil
import socket
import sys
from contextlib import asynccontextmanager
from pathlib import Path

import httpx
import uvicorn
import yaml
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from loguru import logger

ROOT = Path(__file__).resolve().parents[1]
VERSION = "1.2.1-tr.1"
ASR_REPO = "Systran/faster-whisper-small"


def prepare_user_data(data_dir: Path):
    data_dir.mkdir(parents=True, exist_ok=True)
    # Seed only missing data. Updates never overwrite personal content.
    for name in ("live2d-models", "avatars", "backgrounds", "characters", "prompts", "web_tool"):
        source = ROOT / name
        target = data_dir / name
        if not target.exists():
            shutil.copytree(source, target)
    for name in ("model_dict.json", "mcp_servers.json"):
        target = data_dir / name
        if not target.exists():
            if name == "mcp_servers.json":
                target.write_text("{}", "utf-8")
            else:
                shutil.copyfile(ROOT / name, target)
    for name in ("cache", "logs", "models", "chat_history", "frontend"):
        (data_dir / name).mkdir(exist_ok=True)
    target = data_dir / "conf.yaml"
    if not target.exists():
        shutil.copyfile(ROOT / "config_templates/conf.tr-TR.default.yaml", target)


def make_config(settings):
    from src.open_llm_vtuber.config_manager import validate_config
    data = yaml.safe_load(Path("conf.yaml").read_text(encoding="utf-8"))
    data["system_config"].update(host="127.0.0.1", port=0)
    char = data["character_config"]
    basic = char["agent_config"]["agent_settings"]["basic_memory_agent"]
    basic.update(llm_provider="openai_compatible_llm", use_mcpp=False, mcp_enabled_servers=[])
    provider = char["agent_config"]["llm_configs"]["openai_compatible_llm"]
    provider.update(
        base_url=settings.get("baseUrl", "http://127.0.0.1:11434/v1"),
        model=settings.get("model", "configuration-required"),
        llm_api_key=settings.get("apiKey") or "local-no-key",
    )
    char["tts_config"]["edge_tts"]["voice"] = settings.get("voice", "tr-TR-EmelNeural")
    return validate_config(data)


def create_app(settings, token, data_dir):
    from src.open_llm_vtuber.server import WebSocketServer

    server = WebSocketServer(make_config(settings))
    download = {"state": "idle", "message": ""}
    tasks = set()

    def asr_ready():
        folder = data_dir / "models/whisper-small"
        return all((folder / name).is_file() for name in
                   ("model.bin", "config.json", "tokenizer.json", ".tr-ready"))

    @asynccontextmanager
    async def lifespan(app):
        await server.initialize()
        yield
        for task in tasks:
            task.cancel()
        await server.default_context_cache.close()

    app = FastAPI(title="Open-LLM-VTuber TR", lifespan=lifespan)

    @app.get("/tr/health")
    async def health():
        return {"product": "Open-LLM-VTuber TR", "version": VERSION, "ready": True,
                "asrReady": asr_ready(),
                "providerConfigured": bool(settings.get("model"))}

    @app.get("/tr/providers")
    async def providers():
        found = []
        async with httpx.AsyncClient(timeout=2, trust_env=False) as client:
            for name, url in (("Ollama", "http://127.0.0.1:11434/v1"),
                              ("LM Studio", "http://127.0.0.1:1234/v1"),
                              ("OpenAI uyumlu", "http://127.0.0.1:8080/v1")):
                try:
                    response = await client.get(url + "/models")
                    response.raise_for_status()
                    models = [item["id"] for item in response.json().get("data", [])]
                    found.append({"name": name, "baseUrl": url, "models": models})
                except (httpx.HTTPError, ValueError, KeyError):
                    continue
        return found

    @app.get("/tr/asr/status")
    async def asr_status():
        return {**download, "ready": asr_ready()}

    @app.post("/tr/asr/download")
    async def download_asr():
        if download["state"] == "downloading":
            return download
        download.update(state="downloading", message="Türkçe konuşma modeli indiriliyor.")
        async def perform():
            from huggingface_hub import snapshot_download
            download.update(state="downloading", message="Türkçe konuşma modeli indiriliyor.")
            try:
                manifest = json.loads((ROOT / "packaging/asr-model.json").read_text("utf-8"))
                await asyncio.to_thread(
                    snapshot_download, ASR_REPO, revision=manifest["revision"],
                    local_dir=str(data_dir / "models/whisper-small"),
                    allow_patterns=["model.bin", "config.json", "tokenizer.json", "vocabulary.*", "README.md"],
                )
                # Readiness includes real model initialization, not only file existence.
                await asyncio.to_thread(server.default_context_cache.asr_engine._load_model)
                (data_dir / "models/whisper-small/.tr-ready").write_text(manifest["revision"], "utf-8")
                download.update(state="ready", message="Türkçe konuşma modeli hazır.")
            except Exception as exc:
                logger.error("ASR download failed: {}", type(exc).__name__)
                download.update(state="error", message="Model indirilemedi. İnternet bağlantınızı kontrol edip yeniden deneyin.")
        task = asyncio.create_task(perform())
        tasks.add(task)
        task.add_done_callback(tasks.discard)
        return {"state": "downloading"}

    @app.post("/tr/tts/test")
    async def tts_test():
        path = await asyncio.to_thread(
            server.default_context_cache.tts_engine.generate_audio,
            "Merhaba, Open-LLM-VTuber Türkçe ses testi başarılı.")
        if not path or not Path(path).is_file() or Path(path).stat().st_size == 0:
            raise HTTPException(503, "Türkçe ses oluşturulamadı. İnternet bağlantınızı kontrol edin.")
        return FileResponse(path, media_type="audio/mpeg")

    @app.post("/tr/llm/test")
    async def llm_test():
        if not settings.get("model"):
            raise HTTPException(409, "Önce bir yapay zekâ sağlayıcısı seçin.")
        from openai import AsyncOpenAI
        try:
            async with AsyncOpenAI(
                base_url=settings["baseUrl"], api_key=settings.get("apiKey") or "local-no-key",
                timeout=30, max_retries=0,
            ) as client:
                result = await client.chat.completions.create(
                    model=settings["model"],
                    messages=[{"role": "user", "content": "Yalnızca şu kelimeyle cevap ver: TAMAM"}],
                    max_tokens=32,
                )
                return {"text": result.choices[0].message.content}
        except Exception as exc:
            logger.error("Provider test failed: {}", type(exc).__name__)
            raise HTTPException(502, "Yapay zekâ motoruna bağlanılamadı.") from None

    app.mount("/", server.app)

    class AuthenticatedApp:
        async def __call__(self, scope, receive, send):
            if scope["type"] in ("http", "websocket"):
                from urllib.parse import parse_qs
                headers = dict(scope.get("headers", []))
                query = parse_qs(scope.get("query_string", b"").decode())
                supplied = headers.get(b"x-tr-token", b"").decode() or query.get("token", [""])[0]
                if not secrets.compare_digest(supplied, token):
                    if scope["type"] == "websocket":
                        await send({"type": "websocket.close", "code": 1008})
                    else:
                        await send({"type": "http.response.start", "status": 401, "headers": []})
                        await send({"type": "http.response.body", "body": b"Unauthorized"})
                    return
            await app(scope, receive, send)
    return AuthenticatedApp()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, required=True)
    args = parser.parse_args()
    data_dir = args.data_dir.resolve()
    prepare_user_data(data_dir)
    os.chdir(data_dir)
    sys.path.insert(0, str(ROOT))
    os.environ["OPEN_LLM_VTUBER_DESKTOP"] = "1"
    os.environ["HF_HOME"] = str(data_dir / "models/huggingface")
    os.environ["PYTHONUTF8"] = "1"
    # Secrets arrive through an anonymous pipe, never command arguments or log files.
    config = json.loads(sys.stdin.readline())
    token = config["token"]
    api_key = config.get("settings", {}).get("apiKey", "")
    logger.remove()
    def safe_record(record):
        if api_key:
            record["message"] = record["message"].replace(api_key, "[REDACTED]")
        return True
    logger.add(data_dir / "logs/backend.log", level="INFO", rotation="5 MB",
               retention=3, diagnose=False, backtrace=False, filter=safe_record)
    app = create_app(config.get("settings", {}), token, data_dir)
    # OS selects a free port and the same bound socket is passed to Uvicorn (no TOCTOU).
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("127.0.0.1", 0))
    sock.listen(128)
    print(json.dumps({"port": sock.getsockname()[1]}), flush=True)
    async def serve():
        instance = uvicorn.Server(uvicorn.Config(app, log_level="warning", access_log=False))
        async def watch_parent():
            await asyncio.to_thread(sys.stdin.read)
            instance.should_exit = True
        watch = asyncio.create_task(watch_parent())
        try:
            await instance.serve(sockets=[sock])
        finally:
            watch.cancel()
    asyncio.run(serve())


if __name__ == "__main__":
    main()
