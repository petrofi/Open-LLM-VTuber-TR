# Upstream incelemesi — 25 Eylül 2026

## Taban
GitHub Releases üzerinden en yeni prerelease olmayan sürüm v1.2.1 olarak doğrulandı.
Backend: 3afa41014b4548a0842e9ee2f576f4b164b48886.
Frontend build submodule: 06a659b114fff788cf0daaa86e484576db4975bf.
Frontend kaynak v1.2.1: 7a2e214c3f266c294541127520dab7fce46787e7.
TR hedef sürümü: v1.2.1-tr.1. Fork tarihi: 2026-09-25.

main: 992309c0aa19845960228f880013d4685fde93b5; stable sonrasında yeni TTS sağlayıcıları, Docker değişiklikleri ve bağımlılık güncellemeleri içeriyor. Bunlar topluca alınmıyor.
Faster-Whisper initial_prompt düzeltmesi (139c80d) ve boş choices koruması (9a78173) seçilerek değerlendiriliyor.
Frontend sonrasında ses kesme ve motion sınır düzeltmeleri mevcut; regression doğrulamasıyla alınmalı.

## Backend
Python >=3.10,<3.13; .python-version 3.10; uv.lock ve requirements.txt mevcut.
run_server.py konfigürasyonu CWD içindeki conf.yaml üzerinden okuyor; model önbelleğini kaynak dizinine yazıyor; git submodule başlatmaya çalışabiliyor.
ServiceContext.initialize sırasında ASR/TTS/LLM yükleniyor. İlk açılış için ağır modellerden bağımsız bir başlangıç gerekiyor.
FastAPI/WebSocket varsayılan portu 12393; /client-ws ve /asr mevcut; health endpoint yok.
config_templates İngilizce/Çince; Pydantic alanları doğrulanmış Faster-Whisper motorunda language/model_path/device/compute_type mevcut.
Edge TTS mevcut; çevrimiçi ve API anahtarsız. pyttsx3 ses seçimi sunmuyor ve aiff çıktısıyla Windows için doğrulanmış bir Türkçe varsayılan değil.
Backend VAD varsayılanı kapalı; frontend Silero VAD kullanıyor.
Pydub MP3 okuma dış FFmpeg gerektirebilir; Faster-Whisper ile gelen PyAV üzerinden dönüşüm araştırılacak.
Ollama sağlayıcısı açılışta model ön yüklemesi yapıyor; ilk kurulum bitmeden bu kullanılmamalı.
Updater CLI odaklı; config yedekliyor. Paketli uygulamada kaynak/git güncellemesi kullanılmamalı.
Mevcut otomatik unit test klasörü yok. Ruff, FOSSA ve CodeQL iş akışları var.
Release workflow Linux'ta kaynak ZIP üretip ayrı frontend installer'ını alıyor; bütünleşik Windows runtime hazırlamıyor.

## Frontend
Electron 31, React 18, TypeScript 5.5, electron-vite 2/Vite 5, electron-builder 24 ve NSIS.
main: pencere/tray/IPC; preload: contextBridge; renderer: React ve mevcut i18next.
İngilizce/Çince translation.json mevcut; kullanıcı seçimi localStorage'da.
Backend otomatik başlatılmıyor. WebSocket ve HTTP adresleri localStorage'da, başlangıç 127.0.0.1:12393.
Kapat düğmesi uygulamayı tray'e gizliyor; kullanıcı için süreç kapanış davranışı açıklaştırılmalı.
nodeIntegration açık; IPC ve harici URL açma sınırları paketli uygulamada daraltılmalı.
NSIS henüz backend/runtime extraResources içermiyor; paket kimliği örnek com.electron.app.
electron-updater bağımlılığı var, fakat işlevsel TR release kontrolü yok.
Build workflow upstream main push ile draft release ve build branch üretiyor.
Typecheck scriptleri var; unit test scripti yok; lint scripti otomatik --fix uyguluyor.
Harici font dosyası tespit edilmedi. Kaynak ikonlar ve SDK dosyaları ayrı lisans denetimine dahil.

## Yayın izni
Frontend LICENSE, Core LICENSE.md / RedistributableFiles.txt, Framework LICENSE.md ve backend LICENSE-Live2D.md okundu.
Model eklenebilen bu ürün, Live2D'nin Expandable Application tanımıyla örtüşüyor. Proje sahibi 25 Eylül 2026 tarihinde TR fork'unu kapsayan yayın izin belgesine sahip olduğunu bildirdi. Bu beyan esas alınmıştır; özel izin belgesi repoya eklenmez ve belge metni bağımsız olarak incelenmemiştir.
https://www.live2d.com/en/sdk/license/expandable/
https://www.live2d.com/eula/live2d-proprietary-software-license-agreement_en.html
Ücretsiz dağıtım tek başına izin değildir. Başka dağıtıcılar bu izin beyanını kendilerine verilmiş bir izin saymamalıdır.
