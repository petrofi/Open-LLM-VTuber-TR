"""Produce release checksums and Turkish notes from the built artifacts."""
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]


def main():
    metadata = json.loads((ROOT / "UPSTREAM.json").read_text("utf-8"))
    version = metadata["tr_version"]
    output = ROOT / ".dist"
    output.mkdir(exist_ok=True)
    installer = f"Open-LLM-VTuber-TR-v{version}-Setup.exe"
    shutil.copyfile(ROOT / "desktop/release" / version / installer, output / installer)
    sources = "THIRD-PARTY-SOURCES.zip"
    shutil.copyfile(ROOT / ".build" / sources, output / sources)
    hashes = {}
    for name in (installer, sources):
        digest = hashlib.sha256()
        with (output / name).open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
        hashes[name] = digest.hexdigest()
    (output / "SHA256SUMS.txt").write_text(
        "".join(f"{digest}  {name}\n" for name, digest in hashes.items()), "utf-8")
    notes = f"""# Open-LLM-VTuber TR v{version}

Open-LLM-VTuber projesinin resmi olmayan Türkçe topluluk sürümüdür.

## Bu sürümde

- Türkçe arayüz, varsayılan ayarlar ve ilk çalıştırma sihirbazı
- Windows 10/11 x64 için özel Python runtime içeren tek installer
- Backend otomatik başlatma, bağlantı denetimi ve düzgün kapanış
- CPU üzerinde Türkçe Faster-Whisper; kullanıcı seçimiyle model indirme
- Emel/Ahmet Türkçe Edge TTS (çevrimiçi, internet gerekir)
- Yerel LLM algılama, API ayarları ve Windows ile şifrelenmiş anahtar saklama
- TR sürüm kontrolü ve Türkçe hata ekranları

## Kurulum

1. `{installer}` dosyasını indirin.
2. SHA-256 değerini `SHA256SUMS.txt` ile karşılaştırın.
3. Setup.exe'yi çalıştırıp kurulumu tamamlayın.
4. Open-LLM-VTuber TR'yi masaüstü veya Başlat menüsünden açın.

Python, Node.js veya Git kurulması gerekmez. Konuşma modeli ilk kurulumda
kullanıcının seçimiyle indirilir. Bir LLM sağlayıcısı ayrıca yapılandırılır;
installer büyük bir LLM modeli indirmez. Güncelleme ve kaldırma kişisel verileri korur.

**Installer henüz code-sign sertifikasıyla imzalanmamıştır.**

## Upstream

Taban: `{metadata['upstream_tag']}`, commit `{metadata['upstream_commit']}`.
Frontend kaynak tabanı: `{metadata['frontend_source_commit']}`.
Orijinal frontend submodule: `{metadata['frontend_submodule_commit']}`.

## Lisans

Backend MIT, frontend Open-LLM-VTuber License 1.0 kapsamındadır.
Live2D Core, Framework ve örnek modeller kendi koşullarını korur.
TR fork'unu kapsayan yayın izni kullanıcı tarafından teyit edilmiştir.
Tam bildirimler kurulumdaki `resources/licenses` klasöründedir.
FFmpeg/codec kaynakları `THIRD-PARTY-SOURCES.zip` ekinde sunulur.

## SHA-256

`{hashes[installer]}` — `{installer}`
"""
    (output / "release-notes.md").write_text(notes, "utf-8")
    print(installer, hashes[installer])


if __name__ == "__main__":
    main()
