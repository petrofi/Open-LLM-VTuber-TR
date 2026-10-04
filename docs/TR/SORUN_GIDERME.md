# Sorun giderme

**Backend başlatılamadı:** İlk kurulumdaki Logları Aç ve Ayrıntıları Göster alanlarını kullanın. Kurulumu aynı sürüm installer'ı ile yeniden çalıştırın. Kullanıcı verisi otomatik silinmez.

**Yapay zekâ motoruna bağlanılamadı:** Sağlayıcının çalıştığını, API adresini ve model adını denetleyin. Sihirbazdaki bağlantı testini çalıştırın.

**Türkçe konuşma modeli henüz indirilmemiş:** Konuşma Tanıma ekranından indirmeyi başlatın. Yazılı sohbet için ASR modeli zorunlu değildir.

**Model indirmesi yarıda kaldı:** İnternet bağlantınızı kontrol edip aynı düğmeyle yeniden deneyin. İndirme yüzdesi ekranda görünür; tamamlanan dosyalar SHA-256 ile doğrulanır ve tekrar indirilmez. Eksik veya bozuk dosya kullanıma alınmaz.

**Mikrofon erişimi bulunamadı:** Windows izinlerini ve aygıtı kullanıcı olarak kontrol edin; uygulama izinleri değiştirmez.

**Ses oluşmuyor:** Edge TTS çevrimiçidir. İnternet bağlantısını, Windows çıkış aygıtını ve ses karıştırıcısını kontrol edin.

Backend yalnızca loopback üzerinde işletim sisteminin ayırdığı boş porta bağlanır. İstekler uygulamaya özel geçici anahtarla korunur. Sabit port çakışması için başka uygulama kapatmanız gerekmez.

Issue açarken sürümü ve sorunun adımlarını belirtin. API anahtarı, kişisel yollar, sohbet ve ham ayar dosyaları paylaşmayın.
