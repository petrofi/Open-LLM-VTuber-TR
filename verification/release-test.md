# Windows yayın doğrulaması

## Yerel release adayı — 5 Ekim 2026

Upstream: v1.2.1, `3afa41014b4548a0842e9ee2f576f4b164b48886`.
TR sürümü: v1.2.1-tr.1. Backend kaynak: `1c34360`; frontend: `1b77242`.
Gerçek NSIS installer: `Open-LLM-VTuber-TR-v1.2.1-tr.1-Setup.exe`.
Yerel adayın SHA-256 değeri:
`8dfc39f77a69c7de549aabc7b8eeec3a6cf2a33d5caa0d31167de1429061fd53`.

Bu bölüm yerel installer testidir. GitHub Release dosyasının indirilip tekrar
kurulduğu son doğrulama, yayından sonra aşağıya ayrıca kaydedilecektir.

| Kontrol | Sonuç |
| --- | --- |
| Backend Ruff, 7 birim testi, import/config/startup | PASS |
| Frontend lint, TypeScript, 2 locale testi, production build | PASS |
| Özel Python runtime, Electron ve NSIS build | PASS |
| Gerçek kurma, kaldırma, üstüne yeniden kurma | PASS |
| Kullanıcı ayarlarının korunması; tek kurulum kaydı | PASS |
| Masaüstü ve Başlat menüsü kısayolları | PASS |
| Backend bağlantısı ve pencere kapatıldığında süreçlerin sonlanması | PASS |
| Gerçek mikrofon akışı ve frontend VAD | PASS |
| Sihirbazdan model indirme, dosya hashleri ve Türkçe ASR | PASS |
| Türkçe Edge TTS ve frontend ses oynatma | PASS — çevrimiçi |
| Live2D model, idle, ifade ve dudak hareketi | PASS |
| Yerel LLM algılama ve sağlayıcı ayar ekranı | PASS |
| Gerçek LLM yanıtı | CONFIGURATION REQUIRED |
| Güncelleme checksum reddi ve güvenli dosya adı testi | PASS |
| Gizli bilgi ve kişisel kaynak yolu taraması | PASS |

ASR çıktısı: “Merhaba, bu bir Türkçe konuşma tanıma testidir.”
TTS oynatma süresi 4,056 saniye; ses sonuna ulaşıldı.
Live2D idle zamanı ilerledi, `exp_01` ifadesi uygulandı; lip-sync RMS değeri
sıfırdan büyük bulundu. Renderer hatası ve başarısız kaynak isteği yoktu.

## Test ortamı ve sınırlar

Windows 11 Home Single Language x64, 10.0.26300; Intel Core i7-12700H;
32 GB RAM; NVIDIA RTX 4060 Laptop GPU (8188 MiB), sürücü 595.97; Intel Iris Xe.
Varsayılan giriş Mikrofon (Realtek Audio), çıkış Hoparlör (Realtek Audio).
ASR CPU/int8 ile çalıştırıldı; CUDA zorunlu değildir.

Kritik ekranlar 1366×768 ve 1920×1080 pencerelerde, %100 ve %125 Electron
yakınlaştırmasıyla incelendi. Bu, Windows genel DPI ayarını değiştirme testi
değildir. Uzun sihirbaz sayfaları dikey kaydırılabilir; yatay taşma bulunmadı.
Windows 10 hedef platformdur, bu bilgisayarda fiziksel Windows 10 testi yapılmadı.

Ollama, LM Studio veya diğer yerel sağlayıcı bulunmadı; API anahtarı sağlanmadı.
Bu nedenle ASR → gerçek LLM yanıtı → TTS zincirinin LLM bölümü doğrulanamadı.
Ses, ASR, TTS, oynatma ve Live2D ayrı gerçek bileşenlerle doğrulandı.
Installer imzasızdır (`NotSigned`); Windows güvenlik ayarları değiştirilmedi.

## Tekrarlanabilir testler

Backend: `python -m unittest discover -s tests -v`,
`scripts/verify_runtime.py --speech`.
Frontend: `npm run lint`, `npm run typecheck`, `npm test`, `npm run build`.
Paket: `scripts/qa-packaged.cjs`, `scripts/qa-close.cjs`.
Gerçek kurulum: `scripts/verify_installer.ps1`; gerçek ses/görsel test:
`scripts/qa-electron.cjs` (`TR_INSTALLED_EXE`, `TR_ASR_TEST=1`).
Ham loglar ve cihaz verileri repoya eklenmez.
