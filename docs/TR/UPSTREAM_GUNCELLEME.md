# Upstream güncelleme

Önce yeni kararlı GitHub Release'i bulun. Geliştirme main dalını doğrudan ürün tabanı yapmayın.

```bash
git fetch upstream --tags
git switch -c codex/update-upstream
```

Seçilen stable tag'i inceleyin ve bu dalda merge edin. Çakışmalarda copyright ve lisans bildirimlerini koruyun. Frontend kaynak deposunda da aynı sürüme karşılık gelen tag/submodule SHA ilişkisini denetleyin.

Türkçe locale ayrı `tr-TR` dosyasında, masaüstü wrapper'ı ayrı scripts/desktop_server.py ve desktop-runtime.ts dosyalarında tutulur. İngilizce anahtarlara yeni anahtar geldiyse Türkçesini ekleyin; locale testi eksikleri yakalar.

UPSTREAM.json, README ve release notes içindeki tag/SHA kayıtlarını güncelleyin. TR sayacını artırın. Kilitli runtime bağımlılıkları ve tüm lisansları yeniden inceleyin. SDK veya modellerin lisans değişikliklerini ayrıca değerlendirin.

Unit, lint, typecheck, gerçek backend startup, ASR/TTS, Electron ve installer testlerini tekrarlayın. Release'ten gerçek installer'ı tekrar indirip hash doğrulayarak kurun; yalnızca yerel build sonucuna güvenmeyin.

Orijinal prebuilt frontend submodule upstream erişimi için korunur. Windows paketi `desktop` kaynak submodule'ünün kilitli TR commit'inden derlenir. Her iki repoda `upstream` remote orijinal projeyi göstermelidir.
