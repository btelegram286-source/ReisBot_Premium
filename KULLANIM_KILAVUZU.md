# ReisBot Premium - Kullanım Kılavuzu

## 📋 İçindekiler
1. [GitHub Otomatik Yükleme](#github-otomatik-yükleme)
2. [Bot İsmi Değiştirme](#bot-ismi-değiştirme)
3. [YouTube İndirme Sorun Çözümü](#youtube-indirme-sorun-çözümü)
4. [Deployment Seçenekleri](#deployment-seçenekleri)

## 🚀 GitHub Otomatik Yükleme

### Kurulum
1. GitHub'dan Personal Access Token alın:
   - GitHub → Settings → Developer settings → Personal access tokens
   - `repo` yetkilerini verin
   - Token'ı güvenli bir yere kaydedin

2. `config.env` dosyasını düzenleyin:
   ```env
   GITHUB_TOKEN=your_github_token_here
   GITHUB_USER=your_github_username_here
   ```

### Kullanım
```bash
# Tüm dosyaları yükle
github_yukle.bat

# Belirli dosyayı güncelle
github_guncelle.bat main.py

# Dosya sil
github_sil.bat test.py
```

### Komut Satırı
```bash
python auto_updater.py yükle
python auto_updater.py güncelle main.py
python auto_updater.py sil test.py
python auto_updater.py repo_oluştur
python auto_updater.py listele
```

## 🔧 Bot İsmi Değiştirme

### Batch Dosyası ile:
```bash
isim_degistir.bat YeniBotIsmi
```

### Komut Satırı ile:
```bash
python rename_bot.py YeniBotIsmi
```

### Manuel Değişiklikler:
1. `config.env` dosyasındaki açıklamaları güncelleyin
2. Yeni bot token alın (gerekirse)
3. Bağımlılıkları yeniden yükleyin: `pip install -r requirements.txt`

## 🎵 YouTube İndirme Sorun Çözümü

### Otomatik Çözüm:
```bash
youtube_cozum.bat
```

### Manuel Seçenekler:
1. **yt-dlp'ye geçiş** (önerilen):
   ```bash
   pip uninstall youtube-dl -y
   pip install yt-dlp --upgrade
   ```

2. **youtube-dl'ye geri dönüş**:
   ```bash
   pip uninstall yt-dlp -y  
   pip install youtube-dl --upgrade
   ```

3. **FFmpeg Kurulumu**:
   - https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-full.7z
   - `ffmpeg.exe`'yi `C:\Windows\System32\` veya proje dizinine kopyalayın

## 🌐 Deployment Seçenekleri

### Render.com
1. GitHub repository'sini bağlayın
2. Environment variables'ları ayarlayın
3. Build command: `pip install -r requirements.txt`
4. Start command: `python main.py`

### Railway.app
- `railway.json` ve `Procfile` hazır
- Otomatik olarak web panel ve worker olarak deploy eder

### Manuel Deployment
```bash
# Bağımlılıkları yükle
pip install -r requirements.txt

# Environment variables ayarla
set BOT_TOKEN=your_token
set GITHUB_TOKEN=your_github_token
# ... diğer variables'lar

# Botu başlat
python main.py
```

## ⚠️ Sorun Giderme

### Yaygın Sorunlar:
1. **API Anahtarları**: Tüm environment variables'ları kontrol edin
2. **FFmpeg**: YouTube indirme için FFmpeg gerekli
3. **Network**: Internet bağlantınızı kontrol edin
4. **Python Sürümü**: Python 3.8+ gerekiyor

### Log Dosyaları:
- `auto_updater.log` - GitHub işlemleri
- Bot logları - Konsol çıktısında görünür

## 📞 Destek

Sorunlar için:
1. Log dosyalarını kontrol edin
2. Environment variables'ları doğrulayın
3. Internet bağlantınızı test edin
4. Python ve pip sürümlerini kontrol edin

## 🔒 Güvenlik

- API anahtarlarını asla paylaşmayın
- `config.env` dosyasını version control'e eklemeyin
- Düzenli olarak token'ları yenileyin
- Gereksiz yetkiler vermeyin

---

**Not**: Bu araçlar eğitim amaçlıdır. Lütfen telif hakkı yasalarına uygun kullanın.
