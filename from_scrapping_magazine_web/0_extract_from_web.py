#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script d'extraction du vocabulaire web depuis raw_texts
Crée le fichier 1_vocabulaire_web_brut.txt
"""

import re
from pathlib import Path
from collections import Counter

def extract_words(text):
    """Extrait les mots d'un texte"""
    pattern = r"[a-zA-ZàâäéèêëïîôùûüÀÂÄÉÈÊËÏÎÔÙÛÜ]+(?:'[a-zA-ZàâäéèêëïîôùûüÀÂÄÉÈÊËÏÎÔÙÛÜ]+)*"
    return re.findall(pattern, text.lower())

def extract_vocabulary_from_web(raw_texts_dir, bible_file, output_file):
    """Extrait le vocabulaire web qui n'est pas dans la Bible"""
    
    print("=" * 60)
    print("🆕 EXTRACTION VOCABULAIRE WEB")
    print("=" * 60)
    
    # Charger Bible
    with open(bible_file, 'r', encoding='utf-8') as f:
        bible_words = set(line.strip() for line in f if line.strip())
    print(f"📚 Bible : {len(bible_words):,} mots\n")
    
    # Extraire mots du web
    raw_texts_path = Path(raw_texts_dir)
    all_words = []
    file_count = 0
    
    print("📖 Extraction depuis raw_texts...")
    for filepath in sorted(raw_texts_path.glob("*.txt")):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()
                words = extract_words(text)
                all_words.extend(words)
                file_count += 1
                if file_count % 10 == 0:
                    print(f"  Traité : {file_count} fichiers...")
        except Exception as e:
            print(f"⚠️ Erreur {filepath.name}: {e}")
    
    print(f"\n✅ {file_count} fichiers traités")
    
    # Vocabulaire unique
    web_vocab = set(word for word in all_words if len(word) >= 2)
    print(f"🔤 {len(web_vocab):,} mots uniques")
    
    # Nouveaux mots (pas dans Bible)
    new_words = web_vocab - bible_words
    common = web_vocab & bible_words
    
    print(f"\n📊 Analyse :")
    print(f"  Communs  : {len(common):,} mots")
    print(f"  Nouveaux : {len(new_words):,} mots")
    
    # Sauvegarder
    sorted_words = sorted(new_words)
    with open(output_file, 'w', encoding='utf-8') as f:
        for word in sorted_words:
            f.write(word + '\n')
    
    print(f"\n💾 Fichier créé : {output_file}")
    print(f"✨ {len(new_words):,} nouveaux mots extraits")
    print("=" * 60)
    
    # Afficher exemples
    word_freq = Counter(all_words)
    new_with_freq = [(w, word_freq[w]) for w in new_words if w in word_freq]
    new_with_freq.sort(key=lambda x: x[1], reverse=True)
    
    print(f"\n📝 20 mots les plus fréquents :")
    for i, (word, freq) in enumerate(new_with_freq[:20], 1):
        print(f"  {i:2d}. {word:25s} ({freq:3d} fois)")
    
    return len(new_words)

if __name__ == "__main__":
    # Paramètres
    raw_texts_dir = "raw_texts"
    bible_file = "../from_bible_json/vocabulaire_malgache_sans_noms_v2.txt"
    output_file = "1_vocabulaire_web_brut.txt"
    
    # Vérifications
    if not Path(raw_texts_dir).exists():
        print(f"❌ Dossier {raw_texts_dir} introuvable !")
        exit(1)
    
    if not Path(bible_file).exists():
        print(f"❌ Fichier Bible {bible_file} introuvable !")
        exit(1)
    
    # Extraction
    count = extract_vocabulary_from_web(raw_texts_dir, bible_file, output_file)
    print(f"\n🎉 Terminé ! {count:,} nouveaux mots extraits")
