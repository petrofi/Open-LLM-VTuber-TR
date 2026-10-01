# Üçüncü taraf bildirimleri

Ana lisanslar: [NOTICE-TR.md](NOTICE-TR.md) ve [lisans açıklaması](docs/TR/LISANSLAR.md).
Tam kaynak lisansları `packaging/licenses` altında tutulur. Build sırasında kurulu Python paketlerinin lisans dosyaları ile sürüm envanteri ve npm paket bildirimleri installer'ın resources/licenses dizinine kopyalanır. Python, Electron ve Chromium lisansları silinmez.

Ses codec'lerinin sabit kaynak URL ve SHA-256 manifesti [media-sources.json](packaging/media-sources.json) dosyasındadır. Kaynak arşivleri Release'te THIRD-PARTY-SOURCES.zip olarak birlikte sunulur. Bu bileşenlerin copyleft haklarına frontend'in ticari koşulları eklenmez.

Paketlenen örnek Live2D modellerinin kendi ReadMe dosyaları ve LICENSE-Live2D.md korunur. Whisper modeli kullanıcı isteğiyle indirilir; Silero VAD modeli frontend'in mevcut VAD akışı için paketlenir. Model ve SDK hakları TR projesine devredilmiş sayılmaz.
