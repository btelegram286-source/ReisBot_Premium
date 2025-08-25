#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bot İsmi Değiştirme Scripti
ReisBot Premium ismini istediğiniz isimle değiştirir.
"""

import os
import re
import argparse
from pathlib import Path

def replace_in_file(file_path, old_name, new_name):
    """Dosya içeriğindeki isimleri değiştir"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Tüm eski isimleri yeni isimle değiştir
        new_content = content.replace(old_name, new_name)
        
        # Case insensitive değişim (büyük/küçük harf duyarlı)
        new_content = re.sub(
            re.compile(re.escape(old_name), re.IGNORECASE), 
            new_name, 
            new_content
        )
        
        if content != new_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"✅ {file_path} güncellendi")
            return True
        else:
            print(f"ℹ️  {file_path} - Değişiklik gerekmiyor")
            return False
            
    except Exception as e:
        print(f"❌ {file_path} hatası: {e}")
        return False

def rename_files_and_folders(root_dir, old_name, new_name):
    """Dosya ve klasör isimlerini değiştir"""
    changes_made = False
    
    # Önce tüm dosyaları tarayalım
    for root, dirs, files in os.walk(root_dir):
        # Klasör isimlerini değiştir
        for dir_name in dirs[:]:  # Copy of dirs list for modification
            if old_name.lower() in dir_name.lower():
                old_path = os.path.join(root, dir_name)
                new_dir_name = dir_name.replace(old_name, new_name)
                new_dir_name = re.sub(
                    re.compile(old_name, re.IGNORECASE), 
                    new_name, 
                    new_dir_name
                )
                new_path = os.path.join(root, new_dir_name)
                
                try:
                    os.rename(old_path, new_path)
                    print(f"✅ Klasör yeniden adlandırıldı: {dir_name} -> {new_dir_name}")
                    changes_made = True
                    # Update the dirs list to reflect the change
                    dirs[dirs.index(dir_name)] = new_dir_name
                except Exception as e:
                    print(f"❌ Klasör yeniden adlandırma hatası: {e}")
        
        # Dosya isimlerini değiştir
        for file_name in files:
            if old_name.lower() in file_name.lower():
                old_path = os.path.join(root, file_name)
                new_file_name = file_name.replace(old_name, new_name)
                new_file_name = re.sub(
                    re.compile(old_name, re.IGNORECASE), 
                    new_name, 
                    new_file_name
                )
                new_path = os.path.join(root, new_file_name)
                
                try:
                    os.rename(old_path, new_path)
                    print(f"✅ Dosya yeniden adlandırıldı: {file_name} -> {new_file_name}")
                    changes_made = True
                except Exception as e:
                    print(f"❌ Dosya yeniden adlandırma hatası: {e}")
    
    return changes_made

def update_content_in_files(root_dir, old_name, new_name):
    """Dosya içeriklerindeki isimleri değiştir"""
    changes_made = False
    
    # İşlenecek dosya uzantıları
    extensions = ['.py', '.md', '.txt', '.html', '.yml', '.yaml', '.json', '.env', '.bat']
    
    for root, dirs, files in os.walk(root_dir):
        for file_name in files:
            if any(file_name.endswith(ext) for ext in extensions):
                file_path = os.path.join(root, file_name)
                if replace_in_file(file_path, old_name, new_name):
                    changes_made = True
    
    return changes_made

def main():
    parser = argparse.ArgumentParser(description='Bot ismini değiştir')
    parser.add_argument('new_name', help='Yeni bot ismi')
    parser.add_argument('--old-name', default='ReisBot', help='Eski bot ismi (varsayılan: ReisBot)')
    parser.add_argument('--dir', default='.', help='Çalışma dizini (varsayılan: .)')
    
    args = parser.parse_args()
    
    old_name = args.old_name
    new_name = args.new_name
    root_dir = os.path.abspath(args.dir)
    
    print(f"🔧 Bot ismi değiştiriliyor: '{old_name}' -> '{new_name}'")
    print(f"📁 Dizin: {root_dir}")
    print("=" * 50)
    
    # 1. Önce dosya ve klasör isimlerini değiştir
    print("\n📁 Dosya ve klasör isimleri değiştiriliyor...")
    file_changes = rename_files_and_folders(root_dir, old_name, new_name)
    
    # 2. Sonra dosya içeriklerini değiştir
    print("\n📝 Dosya içerikleri güncelleniyor...")
    content_changes = update_content_in_files(root_dir, old_name, new_name)
    
    # 3. Özel dosyaları güncelle
    print("\n🎯 Özel dosyalar güncelleniyor...")
    
    # README.md
    readme_path = os.path.join(root_dir, 'README.md')
    if os.path.exists(readme_path):
        replace_in_file(readme_path, old_name, new_name)
    
    # config.env (BOT_TOKEN description)
    config_path = os.path.join(root_dir, 'config.env')
    if os.path.exists(config_path):
        replace_in_file(config_path, old_name, new_name)
    
    # requirements.txt (opsiyonel paket isimleri)
    req_path = os.path.join(root_dir, 'requirements.txt')
    if os.path.exists(req_path):
        replace_in_file(req_path, old_name, new_name)
    
    print("=" * 50)
    
    if file_changes or content_changes:
        print(f"\n✅ İşlem tamamlandı! Bot ismi '{old_name}' -> '{new_name}' olarak değiştirildi.")
        print("\n📋 Sonraki adımlar:")
        print("1. Gerekli environment variables'ları güncelleyin")
        print("2. Bot token'ını yeniden alın (gerekirse)")
        print("3. Bağımlılıkları yeniden yükleyin: pip install -r requirements.txt")
        print("4. Botu test edin: python main.py")
    else:
        print("\nℹ️  Hiçbir değişiklik yapılmadı. İsim zaten güncel olabilir.")

if __name__ == "__main__":
    main()
