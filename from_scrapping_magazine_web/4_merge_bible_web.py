#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de fusion du vocabulaire Bible + Web
Crée le fichier final avec tous les mots malgaches
"""

from pathlib import Path

def merge_vocabularies(bible_file, web_file, output_file):
    """Fusionne Bible + Web et crée le vocabulaire complet"""
    
    print("=" * 60)
    print("🔀 FUSION VOCABULAIRE BIBLE + WEB")
    print("=" * 60)
    
    # Charger Bible
    with open(bible_file, 'r', encoding='utf-8') as f:
        bible_words = set(line.strip() for line in f if line.strip())
    print(f"📚 Bible   : {len(bible_words):,} mots")
    
    # Charger Web
    with open(web_file, 'r', encoding='utf-8') as f:
        web_words = set(line.strip() for line in f if line.strip())
    print(f"🌐 Web     : {len(web_words):,} mots")
    
    # Fusionner
    total_words = bible_words | web_words
    print(f"🎯 TOTAL   : {len(total_words):,} mots uniques")
    
    # Mots communs et nouveaux
    common = bible_words & web_words
    new_from_web = web_words - bible_words
    
    print(f"\n📊 Analyse :")
    print(f"  Communs    : {len(common):,} mots")
    print(f"  Nouveaux   : {len(new_from_web):,} mots (du web)")
    
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
    web_file = "2_vocabulaire_web_filtre.txt"
    output_file = "5_vocabulaire_malgache_TOTAL.txt"
    
    total = merge_vocabularies(bible_file, web_file, output_file)
    print(f"\n🎉 Mission accomplie ! {total:,} mots au total")
