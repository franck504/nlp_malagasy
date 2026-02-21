#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour télécharger les fichiers depuis Google Colab
À exécuter dans Google Colab après le scraping
"""

from google.colab import files
import shutil
from pathlib import Path

def download_raw_texts():
    """Télécharge tous les fichiers raw_texts en archive ZIP"""
    
    print("=" * 60)
    print("📦 TÉLÉCHARGEMENT DES FICHIERS")
    print("=" * 60)
    
    # Détecter le nom du dossier (raw_texts dans Colab, tononkira_raw_texts localement)
    if Path("raw_texts").exists():
        source_dir = "raw_texts"
    elif Path("tononkira_raw_texts").exists():
        source_dir = "tononkira_raw_texts"
    else:
        print("❌ Aucun dossier de paroles trouvé !")
        print("💡 Exécutez d'abord scraper.py")
        return
    
    # Créer une archive ZIP
    archive_name = "tononkira_raw_texts"
    
    print(f"\n📁 Création de l'archive {archive_name}.zip depuis {source_dir}/...")
    shutil.make_archive(archive_name, 'zip', source_dir)
    
    print(f"💾 Taille: {Path(f'{archive_name}.zip').stat().st_size / 1024 / 1024:.2f} MB")
    
    # Télécharger l'archive
    print(f"\n⬇️ Téléchargement de {archive_name}.zip...")
    files.download(f"{archive_name}.zip")
    
    print("\n✅ Téléchargement terminé !")
    print("=" * 60)

def download_stats():
    """Affiche les statistiques des fichiers"""
    
    # Détecter le nom du dossier
    if Path("raw_texts").exists():
        raw_texts_path = Path("raw_texts")
    elif Path("tononkira_raw_texts").exists():
        raw_texts_path = Path("tononkira_raw_texts")
    else:
        print("❌ Aucun dossier de paroles trouvé !")
        return
    
    files_list = list(raw_texts_path.glob("*.txt"))
    total_size = sum(f.stat().st_size for f in files_list)
    
    print("\n📊 STATISTIQUES")
    print("=" * 60)
    print(f"  Nombre de fichiers : {len(files_list)}")
    print(f"  Taille totale      : {total_size / 1024 / 1024:.2f} MB")
    print(f"  Taille moyenne     : {total_size / len(files_list) / 1024:.2f} KB")
    print("=" * 60)

if __name__ == "__main__":
    download_stats()
    download_raw_texts()
