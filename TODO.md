# Web Dashboard Geliştirme - TODO

Bu dosya, ReisBot için web kontrol panelinin (Flask) geliştirilmesi sırasında adım adım ilerlemeyi takip eder.

## 1) Altyapı ve Bağımlılıklar
- [x] requirements.txt güncelle: Flask ekle
- [ ] Ortam değişkenleri: DASHBOARD_PASSWORD ve WEB_SECRET_KEY ekle (config.env veya env)

## 2) Flask Uygulaması
- [x] Yeni dosya: web_dashboard.py
  - [x] config.env yükle
  - [x] ENV değişkenlerini oku (BOT_TOKEN, GITHUB_TOKEN, GITHUB_USER, RENDER_API_KEY, RENDER_OWNER_ID, DASHBOARD_PASSWORD, WEB_SECRET_KEY)
  - [x] Flask app init + session secret
  - [x] TeleBot init (sadece mesaj göndermek için, polling yok)
  - [x] GitHubManager / RenderManager / PremiumFeatures init (mevcut sınıfları kullan)
  - [x] login_required decorator
  - [x] Güzergahlar (Routes):
    - [x] GET/POST /login
    - [x] GET /logout
    - [x] GET /
    - [x] GET /github/repos
    - [x] POST /github/delete
    - [x] GET /render/services
    - [x] POST /render/deploy
    - [x] GET/POST /message/send
    - [x] GET /stats
    - [x] GET /scheduler
    - [x] POST /scheduler/start
    - [x] POST /scheduler/stop

## 3) HTML Şablonları (templates/)
- [x] base.html (Bootstrap, navbar, flash mesajları)
- [x] login.html (şifre formu)
- [x] dashboard.html (özet bayraklar ve hızlı linkler)
- [x] repos.html (repo listesi ve silme butonları)
- [x] services.html (servis listesi ve deploy butonları)
- [x] send_message.html (chat_id + mesaj formu)
- [x] stats.html (istatistikler)
- [x] scheduler.html (job listesi, start/stop)

## 4) Güvenlik
- [x] Tüm sayfalarda login kontrolü (session)
- [x] Parola ENV üzerinden (DASHBOARD_PASSWORD)
- [x] Secret key ENV (WEB_SECRET_KEY)
- [ ] Gerekiyorsa IP kısıtlama/tek kullanımlık token (ileriki sürüm)

## 5) Çalıştırma ve Doğrulama
- [ ] `python web_dashboard.py` ile başlat (port 5000)
- [ ] Login test
- [ ] GitHub repo liste / sil test
- [ ] Render servis liste / deploy test
- [ ] Bot ile mesaj gönderme testi
- [ ] Stats görüntüleme testi
- [ ] Scheduler start/stop ve job list testi

## 6) Scheduler Web Dashboard Entegrasyonu
- [x] WEB_DASHBOARD_URL environment variable eklendi
- [x] Tüm scheduler fonksiyonlarına web dashboard URL'si eklendi:
  - [x] daily_backup() - Günlük yedekleme bildirimleri
  - [x] auto_github_push() - Otomatik GitHub push bildirimleri
  - [x] auto_render_deploy() - Otomatik Render deploy bildirimleri
  - [x] weekly_report() - Haftalık rapor bildirimleri
  - [x] health_check() - Sistem uyarı bildirimleri

## Notlar
- main.py import edilmeyecek (polling tetiklenmesin)
- Scheduler varsayılan kapalı, manuel başlat/sonlandır
- PremiumFeatures sqlite db (reisbot_premium.db) aynı dizinde kullanılacak
- Web dashboard URL'si: `WEB_DASHBOARD_URL` environment variable olarak ayarlanmalı
- Tüm scheduler bildirimlerinde web panel linki gösteriliyor
