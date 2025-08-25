# -*- coding: utf-8 -*-
import schedule
import time
import threading
import logging
from datetime import datetime
from github_manager import GitHubManager
from render_manager import RenderManager
import os

logger = logging.getLogger(__name__)

class BotScheduler:
    def __init__(self, bot, github_manager, render_manager):
        self.bot = bot
        self.github_manager = github_manager
        self.render_manager = render_manager
        self.running = False
        self.scheduler_thread = None
        # Named job tanımları (in-memory). {tag: {"job_type":..., "time_spec":..., "function_key":...}}
        self.job_defs = {}
        
    def start_scheduler(self):
        """Scheduler'ı başlat"""
        if not self.running:
            self.running = True
            self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
            self.scheduler_thread.start()
            logger.info("🕐 Scheduler başlatıldı!")
    
    def stop_scheduler(self):
        """Scheduler'ı durdur"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join()
        logger.info("🛑 Scheduler durduruldu!")
    
    def _run_scheduler(self):
        """Scheduler ana döngüsü"""
        while self.running:
            schedule.run_pending()
            time.sleep(60)  # Her dakika kontrol et
    
    def setup_default_jobs(self):
        """Varsayılan cron job'ları ayarla"""
        
        # Her gün saat 02:00'da otomatik backup
        schedule.every().day.at("02:00").do(self.daily_backup)
        
        # Her 6 saatte bir GitHub'a otomatik push
        schedule.every(6).hours.do(self.auto_github_push)
        
        # Her 12 saatte bir Render deploy
        schedule.every(12).hours.do(self.auto_render_deploy)
        
        # Her hafta Pazartesi saat 09:00'da haftalık rapor
        schedule.every().monday.at("09:00").do(self.weekly_report)
        
        # Her saat başı sistem durumu kontrolü
        schedule.every().hour.do(self.health_check)
        
        logger.info("📅 Varsayılan cron job'lar ayarlandı!")
    
    def daily_backup(self):
        """Günlük yedekleme"""
        try:
            logger.info("🔄 Günlük yedekleme başlatılıyor...")
            
            # GitHub'a push
            result = self.github_manager.upload_current_bot("ReisBot_Premium_Backup")
            
            # Admin'e bildirim gönder (config'den admin chat ID alınabilir)
            admin_chat_id = os.getenv("ADMIN_CHAT_ID")
            if admin_chat_id:
                web_dashboard_url = os.getenv("WEB_DASHBOARD_URL", "")
                message = f"""
🔄 *Günlük Otomatik Yedekleme*

📅 Tarih: {datetime.now().strftime('%Y-%m-%d %H:%M')}
📁 GitHub Backup: Tamamlandı
📊 Durum: ✅ Başarılı

{result}

🌐 Panel: {web_dashboard_url}
                """
                self.bot.send_message(admin_chat_id, message, parse_mode='Markdown')
            
            logger.info("✅ Günlük yedekleme tamamlandı!")
            
        except Exception as e:
            logger.error(f"❌ Günlük yedekleme hatası: {e}")
    
    def auto_github_push(self):
        """Otomatik GitHub push"""
        try:
            logger.info("🔄 Otomatik GitHub push başlatılıyor...")
            
            result = self.github_manager.upload_current_bot("ReisBot_Premium")
            
            admin_chat_id = os.getenv("ADMIN_CHAT_ID")
            if admin_chat_id:
                web_dashboard_url = os.getenv("WEB_DASHBOARD_URL", "")
                message = f"""
🔄 *Otomatik GitHub Push*

📅 Tarih: {datetime.now().strftime('%Y-%m-%d %H:%M')}
📁 Repository: ReisBot_Premium
📊 Durum: ✅ Başarılı

{result}

🌐 Panel: {web_dashboard_url}
                """
                self.bot.send_message(admin_chat_id, message, parse_mode='Markdown')
            
            logger.info("✅ Otomatik GitHub push tamamlandı!")
            
        except Exception as e:
            logger.error(f"❌ Otomatik GitHub push hatası: {e}")
    
    def auto_render_deploy(self):
        """Otomatik Render deploy"""
        try:
            logger.info("🔄 Otomatik Render deploy başlatılıyor...")
            
            services = self.render_manager.get_services()
            results = []
            
            for service in services:
                if 'reisbot' in service['name'].lower():
                    result = self.render_manager.deploy_service(service['id'])
                    results.append(f"{service['name']}: {result}")
            
            admin_chat_id = os.getenv("ADMIN_CHAT_ID")
            if admin_chat_id:
                web_dashboard_url = os.getenv("WEB_DASHBOARD_URL", "")
                message = f"""
🔄 *Otomatik Render Deploy*

📅 Tarih: {datetime.now().strftime('%Y-%m-%d %H:%M')}
🚀 Deploy Sonuçları:

{chr(10).join(results) if results else 'Hiç servis bulunamadı'}

🌐 Panel: {web_dashboard_url}
                """
                self.bot.send_message(admin_chat_id, message, parse_mode='Markdown')
            
            logger.info("✅ Otomatik Render deploy tamamlandı!")
            
        except Exception as e:
            logger.error(f"❌ Otomatik Render deploy hatası: {e}")
    
    def weekly_report(self):
        """Haftalık rapor"""
        try:
            logger.info("📊 Haftalık rapor oluşturuluyor...")
            
            # GitHub istatistikleri
            repos = self.github_manager.list_repositories()
            
            # Render servisleri
            services = self.render_manager.get_services()
            
            admin_chat_id = os.getenv("ADMIN_CHAT_ID")
            if admin_chat_id:
                web_dashboard_url = os.getenv("WEB_DASHBOARD_URL", "")
                message = f"""
📊 *Haftalık ReisBot Raporu*

📅 Tarih: {datetime.now().strftime('%Y-%m-%d %H:%M')}

📁 *GitHub İstatistikleri:*
• Toplam Repository: {len(repos)}
• Aktif Projeler: {len([r for r in repos if not r['private']])}

🚀 *Render Servisleri:*
• Toplam Servis: {len(services)}
• Aktif Servisler: {len([s for s in services if s['status'] == 'active'])}

✅ *Sistem Durumu:* Çalışıyor
🔄 *Son Güncelleme:* {datetime.now().strftime('%Y-%m-%d %H:%M')}

🌐 Panel: {web_dashboard_url}

Bu rapor her Pazartesi otomatik olarak gönderilir.
                """
                self.bot.send_message(admin_chat_id, message, parse_mode='Markdown')
            
            logger.info("✅ Haftalık rapor gönderildi!")
            
        except Exception as e:
            logger.error(f"❌ Haftalık rapor hatası: {e}")
    
    def health_check(self):
        """Sistem sağlık kontrolü"""
        try:
            logger.info("🔍 Sistem sağlık kontrolü yapılıyor...")
            
            # Basit sağlık kontrolü
            issues = []
            
            # GitHub bağlantısı kontrol et
            try:
                repos = self.github_manager.list_repositories()
                if not repos:
                    issues.append("GitHub bağlantısı sorunlu olabilir")
            except:
                issues.append("GitHub API hatası")
            
            # Render servisleri kontrol et
            try:
                services = self.render_manager.get_services()
                inactive_services = [s for s in services if s['status'] != 'active']
                if inactive_services:
                    issues.append(f"{len(inactive_services)} servis aktif değil")
            except:
                issues.append("Render API hatası")
            
            # Kritik sorun varsa admin'e bildir
            if issues:
                admin_chat_id = os.getenv("ADMIN_CHAT_ID")
                if admin_chat_id:
                    web_dashboard_url = os.getenv("WEB_DASHBOARD_URL", "")
                    message = f"""
⚠️ *Sistem Uyarısı*

📅 Tarih: {datetime.now().strftime('%Y-%m-%d %H:%M')}

🚨 *Tespit Edilen Sorunlar:*
{chr(10).join([f"• {issue}" for issue in issues])}

🌐 Panel: {web_dashboard_url}

Lütfen kontrol edin!
                    """
                    self.bot.send_message(admin_chat_id, message, parse_mode='Markdown')
            
            logger.info("✅ Sistem sağlık kontrolü tamamlandı!")
            
        except Exception as e:
            logger.error(f"❌ Sağlık kontrolü hatası: {e}")
    
    def add_custom_job(self, job_type, time_spec, function, *args, **kwargs):
        """Özel cron job ekle"""
        try:
            if job_type == "daily":
                schedule.every().day.at(time_spec).do(function, *args, **kwargs)
            elif job_type == "hourly":
                schedule.every().hour.do(function, *args, **kwargs)
            elif job_type == "weekly":
                day, time = time_spec.split(" ")
                getattr(schedule.every(), day.lower()).at(time).do(function, *args, **kwargs)
            elif job_type == "interval":
                interval = int(time_spec)
                schedule.every(interval).minutes.do(function, *args, **kwargs)
            
            logger.info(f"✅ Özel job eklendi: {job_type} - {time_spec}")
            return True
        except Exception as e:
            logger.error(f"❌ Özel job ekleme hatası: {e}")
            return False
    
    def list_jobs(self):
        """Aktif job'ları listele"""
        jobs = []
        for job in schedule.jobs:
            jobs.append({
                'function': job.job_func.__name__,
                'interval': str(job.interval),
                'unit': job.unit,
                'next_run': job.next_run.strftime('%Y-%m-%d %H:%M') if job.next_run else 'Bilinmiyor',
                'tags': list(job.tags) if hasattr(job, 'tags') else []
            })
        return jobs
    
    def clear_all_jobs(self):
        """Tüm job'ları temizle"""
        schedule.clear()
        logger.info("🗑️ Tüm cron job'lar temizlendi!")

    # ==== Named job yönetimi (tag destekli) ====

    def _map_function_key(self, key):
        """UI'dan gelen function_key'i gerçek metoda map et"""
        mapping = {
            'daily_backup': self.daily_backup,
            'auto_github_push': self.auto_github_push,
            'auto_render_deploy': self.auto_render_deploy,
            'weekly_report': self.weekly_report,
            'health_check': self.health_check,
        }
        return mapping.get(key)

    def add_named_job(self, tag, job_type, time_spec, function_key):
        """
        Tag'li özel cron job ekle.
        job_type: daily | hourly | weekly | interval
        time_spec: 
          - daily: "HH:MM"
          - hourly: ignore (boş bırakılabilir)
          - weekly: "monday 09:00" (gün boşluk saat)
          - interval: "15" (dakika)
        function_key: daily_backup | auto_github_push | auto_render_deploy | weekly_report | health_check
        """
        try:
            func = self._map_function_key(function_key)
            if not func:
                logger.error(f"Geçersiz function_key: {function_key}")
                return False

            # Schedule ekle ve tag ata
            if job_type == "daily":
                schedule.every().day.at(time_spec).do(func).tag(tag)
            elif job_type == "hourly":
                schedule.every().hour.do(func).tag(tag)
            elif job_type == "weekly":
                day, t = time_spec.split(" ")
                getattr(schedule.every(), day.lower()).at(t).do(func).tag(tag)
            elif job_type == "interval":
                interval = int(time_spec)
                schedule.every(interval).minutes.do(func).tag(tag)
            else:
                logger.error(f"Geçersiz job_type: {job_type}")
                return False

            # Def'i sakla
            self.job_defs[tag] = {
                "job_type": job_type,
                "time_spec": time_spec,
                "function_key": function_key
            }
            logger.info(f"✅ Named job eklendi: {tag} ({job_type} - {time_spec} - {function_key})")
            return True
        except Exception as e:
            logger.error(f"❌ Named job ekleme hatası: {e}")
            return False

    def remove_job(self, tag):
        """Job'u tamamen sil (takvimden ve kayıtlı defs'ten)"""
        try:
            schedule.clear(tag)
            if tag in self.job_defs:
                del self.job_defs[tag]
            logger.info(f"🗑️ Job silindi: {tag}")
            return True
        except Exception as e:
            logger.error(f"❌ Job silme hatası: {e}")
            return False

    def stop_job(self, tag):
        """Job'u takvimden kaldır ama tanımı (job_defs) sakla"""
        try:
            schedule.clear(tag)
            logger.info(f"⏸️ Job durduruldu: {tag}")
            return True
        except Exception as e:
            logger.error(f"❌ Job durdurma hatası: {e}")
            return False

    def start_job(self, tag):
        """Önceden tanımlı job'u (job_defs) yeniden takvime ekle"""
        try:
            if tag not in self.job_defs:
                logger.error(f"Tanım yok: {tag}")
                return False
            jd = self.job_defs[tag]
            return self.add_named_job(tag, jd["job_type"], jd["time_spec"], jd["function_key"])
        except Exception as e:
            logger.error(f"❌ Job başlatma hatası: {e}")
            return False

    def run_job_now(self, tag):
        """Job ile ilişkili fonksiyonu hemen çalıştır"""
        try:
            if tag not in self.job_defs:
                logger.error(f"Tanım yok: {tag}")
                return False
            func = self._map_function_key(self.job_defs[tag]["function_key"])
            if not func:
                return False
            func()
            logger.info(f"⚡ Job anında çalıştırıldı: {tag}")
            return True
        except Exception as e:
            logger.error(f"❌ Anında çalıştırma hatası: {e}")
            return False
