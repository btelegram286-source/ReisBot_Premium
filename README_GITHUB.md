# ReisBot Premium - GitHub Otomatik Güncelleme Sistemi

Bu sistem, ReisBot Premium projesini GitHub'a otomatik olarak yüklemenizi, güncellemenizi ve yönetmenizi sağlar.

## Kurulum

1. **GitHub Token Oluşturun:**
   - GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
   - "Generate new token" → "Generate new token (classic)"
   - İzinler: `repo` (tüm repo yetkileri)
   - Token'ı güvenli bir yere kaydedin

2. **Config Dosyasını Düzenleyin:**
   - `config.env` dosyasını açın
   - Aşağıdaki değerleri güncelleyin:
     ```
     GITHUB_TOKEN=oluşturduğunuz_token_buraya
     GITHUB_USER=github_kullanıcı_adınız
     ```

## Kullanım

### Komut Satırından:
```bash
# Tüm dosyaları yükle
python auto_updater.py yükle

# Belirli dosyayı güncelle
python auto_updater.py güncelle main.py

# Dosya sil
python auto_updater.py sil test.py

# Yeni repository oluştur
python auto_updater.py repo_oluştur

# Repository'leri listele
python auto_updater.py listele
```

### Batch Dosyası Kullanarak:
- `github_yukle.bat` - Tüm dosyaları yükler
- `github_guncelle.bat` - Belirli dosyayı günceller
- `github_sil.bat` - Dosya siler

## Desteklenen Dosyalar

- Ana dosyalar: `.py`, `.txt`, `.md`, `.env`, `.bat`, `.yaml`, `.json`
- Template dosyaları: `.html` (templates klasörü içinde)
- Config dosyaları

## Önemli Notlar

1. İlk kullanımdan önce mutlaka GitHub token oluşturun
2. Repository otomatik olarak oluşturulacaktır (eğer yoksa)
3. Dosyalar güncel değilse güncellenir, yoksa oluşturulur
4. Loglar `auto_updater.log` dosyasına kaydedilir

## Hata Durumunda

1. Token'ı kontrol edin
2. Internet bağlantınızı kontrol edin
3. Log dosyasını inceleyin: `auto_updater.log`
