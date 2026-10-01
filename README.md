# Open-LLM-VTuber TR

**Open-LLM-VTuber projesinin resmi olmayan Türkçe topluluk sürümüdür.**
Ücretsizdir. Orijinal proje: [Open-LLM-VTuber](https://github.com/Open-LLM-VTuber/Open-LLM-VTuber).

## Windows'a kurulum

[Releases](https://github.com/petrofi/Open-LLM-VTuber-TR/releases) sayfasından
**Open-LLM-VTuber-TR-v1.2.1-tr.1-Setup.exe** dosyasını indirin → kurun → masaüstündeki **Open-LLM-VTuber TR** simgesine çift tıklayın.
Python, Node.js, Git veya terminal kullanmanız gerekmez. Uygulama kendi backend'ini başlatır.
Installer henüz code-sign sertifikasıyla imzalanmamıştır.

İlk açılışta Türkçe sihirbaz mikrofonu, hoparlörü ve yapay zekâ sağlayıcısını ayarlar.
Konuşma tanıma için yaklaşık 465 MB model, yalnızca **Türkçe Konuşma Modelini İndir** düğmesine bastığınızda indirilir.
Büyük bir LLM modeli otomatik indirilmez. Bir sağlayıcı seçmeden arayüzü açabilirsiniz; sohbet yanıtı için sağlayıcı gerekir.

## Gereksinimler

Windows 10 veya 11 x64, en az 8 GB RAM ve 4 GB boş disk alanı önerilir; yerel LLM için modelin ek gereksinimleri geçerlidir.
GPU zorunlu değildir. Faster-Whisper small, CPU/int8 ve Türkçe dil ayarıyla çalışır.
Sesli sohbet için Windows tarafından erişilebilen mikrofon ve hoparlör/kulaklık gerekir. Yazılı sohbet mikrofon istemez.
İlk model indirmesi ve varsayılan Edge seslendirme için internet gerekir. Edge TTS, seslendirilecek metni Microsoft hizmetine gönderir; API anahtarı istemez.

Ollama, LM Studio ve yerel OpenAI uyumlu sunucular otomatik aranır. Bulut için OpenAI uyumlu HTTPS API adresi, model adı ve kendi API anahtarınız kullanılabilir.
API anahtarı Windows hesabına bağlı Electron safeStorage ile şifrelenir; repoya veya loglara yazılmaz.
Türkçe varsayılandır; ayarlardan English seçilebilir.

## Upstream tabanı

- Kararlı upstream: **v1.2.1**
- Backend commit: `3afa41014b4548a0842e9ee2f576f4b164b48886`
- Orijinal frontend build submodule: `06a659b114fff788cf0daaa86e484576db4975bf`
- Frontend kaynak tag v1.2.1: `7a2e214c3f266c294541127520dab7fce46787e7`
- Fork oluşturma tarihi: **2026-09-25**
- TR sürümü: **v1.2.1-tr.1**

Geliştirme main dalı yerine kararlı sürüm temel alınmıştır. İnceleme ve seçilen düzeltmeler [upstream analizinde](docs/TR/UPSTREAM_ANALIZI.md) kayıtlıdır.
[İngilizce upstream README](README.EN.md) korunmuştur. [Frontend kaynak fork'u](https://github.com/petrofi/Open-LLM-VTuber-Web-TR).

## Yardım

[İlk kurulum](docs/TR/ILK_KURULUM.md) · [LLM ayarları](docs/TR/LLM_AYARLARI.md) · [Mikrofon](docs/TR/MIKROFON.md) · [Seslendirme](docs/TR/TTS.md) · [Sorun giderme](docs/TR/SORUN_GIDERME.md)

Kişisel ayarlar, sohbetler ve modeller `%APPDATA%/Open-LLM-VTuber-TR` altında tutulur. Güncelleme ve normal kaldırma bunları silmez.

## Lisanslar ve kaynak

Backend [MIT](LICENSE); frontend **Open-LLM-VTuber License 1.0** (Apache 2.0 temeli ve ek ticari koşullar); Live2D Core, Framework ve örnek modeller ayrı koşullara tabidir.
Bu paket tümüyle MIT lisanslı olarak sunulmaz. Orijinal copyright ve lisanslar korunur.
[Atıflar](NOTICE-TR.md) · [Ayrıntılı lisanslar](docs/TR/LISANSLAR.md) · [Üçüncü taraflar](THIRD_PARTY_LICENSES.md).
Dağıtılan copyleft codec kaynakları Release'teki **THIRD-PARTY-SOURCES.zip** dosyasında sağlanır.

[Geliştirici kurulumu](docs/TR/GELISTIRICI.md) ve [upstream güncelleme yöntemi](docs/TR/UPSTREAM_GUNCELLEME.md) son kullanıcı kurulumundan ayrıdır.
