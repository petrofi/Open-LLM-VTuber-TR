# Geliştirici kurulumu ve Windows build

Son kullanıcı Setup.exe kullanır. Aşağıdaki araçlar yalnızca geliştirici makinesi ve CI içindir.

Backend deposunu submodule'leriyle klonlayın. Python 3.10.20 için uygulamaya özel uv managed runtime oluşturun; sistem Python'una paket kurmayın. Windows release workflow'u aynı adımları otomatik uygular.

```powershell
uv python install 3.10.20 --install-dir .build/python
uv venv .venv --python .build/python/cpython-3.10.20-windows-x86_64-none/python.exe
uv pip install --python .venv/Scripts/python.exe --require-hashes -r packaging/requirements-runtime.txt
.venv/Scripts/python.exe -m unittest discover -s tests -v
.venv/Scripts/python.exe scripts/verify_runtime.py
.venv/Scripts/python.exe scripts/stage_desktop.py --frontend desktop
```

Frontend içinde `npm ci`, `npm run lint`, `npm run typecheck`, `npm test`, `npm run build` ve `npm run build:win` çalıştırılır. Node 24 kullanılır. `node scripts/collect-licenses.cjs` üçüncü taraf bildirimlerini toplar. Release derlemesinde internet gerektiren gerçek ses testi ayrıca çalıştırılır: `scripts/verify_runtime.py --speech`.

SDK tip bildirimleri ayrı upstream uyumlu projede üretilir; uygulama TypeScript strict kontrolünden geçer. Electron kaynak runtime yolu geliştirmede kardeş `Open-LLM-VTuber-TR` dizinidir; paketlemede resources/backend ve resources/python kullanılır.

`packaging/requirements-runtime.txt` SHA-256 kilitleriyle sınırlandırılmış Windows CPU bağımlılık kümesidir. Upstream `pyproject.toml` ve `uv.lock` tam geliştirici kurulumu için korunur. Temel backend Ruff kontrolü upstream sürümü 0.8.6 ile yapılır.

Yeni sürümde hem backend desktop VERSION hem frontend package.json/runtime sürümü ve UPSTREAM.json güncellenmelidir. Kişisel loglar `.build`, `.qa` ve `.runtime` altında kalır; commit edilmez.
