# Yapay zekâ motoru

Ollama için `http://127.0.0.1:11434/v1`, LM Studio için `http://127.0.0.1:1234/v1` ve diğer yerel OpenAI uyumlu servisler için `http://127.0.0.1:8080/v1` taranır. Çalışan modeller listelenir. Başka bir yerel port da API adresi alanına girilebilir.

Yerel sağlayıcınızı çalıştırın ve modeli o sağlayıcının arayüzünde kurun. Model adı sunucunun sunduğu adla aynı olmalıdır. Mevcut modeller silinmez veya değiştirilmez.

Bulut API için HTTPS adresi, model ve size ait anahtar gerekir. Kaydet ve Bağlantıyı Dene, modele “Yalnızca şu kelimeyle cevap ver: TAMAM” isteği gönderir. Test ücretli sağlayıcıda küçük bir kullanım ücreti doğurabilir.

Anahtar Electron safeStorage ile Windows hesabınıza bağlı şifrelenir. `settings.json` ve sohbetleri paylaşmayın. Anahtarı README, issue veya loglara yapıştırmayın. Yerel servis için anahtar gerekmez. Bu Windows paketi OpenAI uyumlu LLM + Faster-Whisper + Edge TTS akışına odaklanır; upstream'in diğer isteğe bağlı motorları geliştirici kurulumunda kullanılabilir.
