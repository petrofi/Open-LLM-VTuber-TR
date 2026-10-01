# Türkçe seslendirme

Varsayılan motor upstream'in desteklediği Edge TTS'dir. Emel ve Ahmet Türkçe sesleri sunulur. API anahtarı gerekmez, ancak internet gerekir ve metin Microsoft'un ses hizmetine iletilir. Üçüncü taraf hizmetin erişilebilirliği değişebilir.

Türkçe Sesi Dene düğmesi “Merhaba, Open-LLM-VTuber Türkçe ses testi başarılı.” cümlesini üretir. Ses dosyası boşsa veya hizmete ulaşılamazsa Türkçe hata gösterilir.

MP3 çözümleme paketlenmiş PyAV/FFmpeg kütüphaneleriyle yapılır. Son kullanıcı ayrıca FFmpeg kurmaz. Arayüze WAV ve dudak hareketi için ses seviyesi dizisi gönderilir.
