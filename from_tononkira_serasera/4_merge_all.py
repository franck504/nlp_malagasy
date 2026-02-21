#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de fusion Bible + Web + Paroles de chansons
Crée le fichier final avec TOUS les mots malgaches
"""

from pathlib import Path

def merge_all_vocabularies(bible_file, web_file, lyrics_file, output_file):
    """Fusionne Bible + Web + Paroles et crée le vocabulaire COMPLET"""
    
    print("=" * 60)
    print("🔀 FUSION BIBLE + WEB + PAROLES")
    print("=" * 60)
    
    # Charger Bible
    with open(bible_file, 'r', encoding='utf-8') as f:
        bible_words = set(line.strip() for line in f if line.strip())
    print(f"📚 Bible      : {len(bible_words):,} mots")
    
    # Charger Web
    with open(web_file, 'r', encoding='utf-8') as f:
        web_words = set(line.strip() for line in f if line.strip())
    print(f"🌐 Web        : {len(web_words):,} mots")
    
    # Charger Paroles
    with open(lyrics_file, 'r', encoding='utf-8') as f:
        lyrics_words = set(line.strip() for line in f if line.strip())
    print(f"🎵 Paroles    : {len(lyrics_words):,} mots")
    
    # Fusionner TOUT
    total_words = bible_words | web_words | lyrics_words
    print(f"🎯 TOTAL      : {len(total_words):,} mots uniques")
    
    # Statistiques
    print(f"\n📊 Analyse :")
    only_bible = bible_words - web_words - lyrics_words
    only_web = web_words - bible_words - lyrics_words
    only_lyrics = lyrics_words - bible_words - web_words
    
    print(f"  Bible uniquement      : {len(only_bible):,} mots")
    print(f"  Web uniquement        : {len(only_web):,} mots")
    print(f"  Paroles uniquement    : {len(only_lyrics):,} mots")
    
    # Sauvegarder
    sorted_words = sorted(total_words)
    with open(output_file, 'w', encoding='utf-8') as f:
        for word in sorted_words:
            f.write(word + '\n')
    
    print(f"\n💾 Fichier créé : {output_file}")
    print(f"✅ {len(total_words):,} mots malgaches uniques !")
    print("=" * 60)
    
    return len(total_words)

if __name__ == "__main__":
    # Chemins des fichiers
    bible_file = "../from_bible_json/vocabulaire_malgache_sans_noms_v2.txt"
    web_file = "../from_scrapping_magazine_web/2_vocabulaire_web_filtre.txt"
    lyrics_file = "2_vocabulaire_lyrics_filtre.txt"
    output_file = "5_vocabulaire_malgache_COMPLET.txt"
    
    # Vérifications
    for f in [bible_file, web_file, lyrics_file]:
        if not Path(f).exists():
            print(f"❌ Fichier introuvable : {f}")
            exit(1)
    
    total = merge_all_vocabularies(bible_file, web_file, lyrics_file, output_file)
    print(f"\n🎉 Mission accomplie ! {total:,} mots au total")
