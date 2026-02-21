#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 5 : Nettoyage et Purification du Corpus
Filtre les phrases non-malgaches (Français, Anglais) et normalise le texte.
"""

import argparse
import re
from pathlib import Path

# Listes de mots outils pour la détection de langue
MG_STOPWORDS = {
    "ny", "dia", "no", "sy", "ao", "eo", "tao", "teo", "koa", "raha", "fa", "nefa", 
    "miaraka", "amina", "amin", "an", "izany", "izay", "ity", "ireto", "aho", "ianao", 
    "isika", "izahay", "ianareo", "izy", "ireo", "mila", "tokony", "misy", "tsy"
}

FR_STOPWORDS = {
    "le", "la", "les", "de", "du", "des", "je", "tu", "il", "nous", "vous", "ils", 
    "est", "et", "pour", "dans", "un", "une", "avec", "sur", "ce", "c'est", "que", "qui"
}

EN_STOPWORDS = {
    "the", "is", "at", "which", "on", "and", "to", "of", "a", "in", "that", "it", 
    "you", "i", "my", "your", "for", "with", "as", "are", "be"
}

def detect_language_simple(text):
    """
    Détecte si le texte est majoritairement malgache.
    Retourne 'mg', 'fr', 'en' ou 'unknown'.
    """
    words = re.findall(r'\b\w+\b', text.lower())
    if not words:
        return 'unknown'
    
    mg_count = sum(1 for w in words if w in MG_STOPWORDS)
    fr_count = sum(1 for w in words if w in FR_STOPWORDS)
    en_count = sum(1 for w in words if w in EN_STOPWORDS)
    
    # Priorité au Malgache si présent
    if mg_count > fr_count and mg_count > en_count:
        return 'mg'
    elif fr_count > mg_count and fr_count > en_count:
        return 'fr'
    elif en_count > mg_count and en_count > fr_count:
        return 'en'
    
    return 'mg' if mg_count > 0 else 'unknown'

def clean_text(text):
    """Normalisation de base."""
    # Supprimer les répétitions de ponctuation
    text = re.sub(r'([!?.]){2,}', r'\1', text)
    # Supprimer les espaces multiples
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def process_corpus(input_file, output_file, threshold=0.1):
    """
    Traite le corpus pour ne garder que le malgache.
    Traite bloc par bloc (séparés par \n\n).
    """
    input_path = Path(input_file)
    output_path = Path(output_file)

    if not input_path.exists():
        print(f"❌ Fichier d'entrée {input_file} introuvable !")
        return

    print("=" * 70)
    print("🧹 PURIFICATION DU CORPUS")
    print(f"   Entrée : {input_file}")
    print(f"   Sortie : {output_file}")
    print("=" * 70)

    stats = {"total_blocks": 0, "kept_mg": 0, "removed_fr": 0, "removed_en": 0, "removed_unknown": 0}

    with open(input_path, "r", encoding="utf-8") as fin, \
         open(output_path, "w", encoding="utf-8") as fout:
        
        # On lit par blocs séparés par une ligne vide (une chanson dans notre corpus fusionné)
        content = fin.read()
        blocks = content.split("\n\n")
        stats["total_blocks"] = len(blocks)

        for block in blocks:
            if not block.strip():
                continue
            
            lang = detect_language_simple(block)
            
            if lang == 'mg':
                cleaned = clean_text(block)
                if len(cleaned) > 20: # Filtrer les phrases trop courtes
                    fout.write(cleaned + "\n\n")
                    stats["kept_mg"] += 1
                else:
                    stats["removed_unknown"] += 1
            elif lang == 'fr':
                stats["removed_fr"] += 1
            elif lang == 'en':
                stats["removed_en"] += 1
            else:
                stats["removed_unknown"] += 1

    print(f"📊 RÉSULTATS :")
    print(f"   Total blocs analysés : {stats['total_blocks']}")
    print(f"   ✅ Blocs MG gardés   : {stats['kept_mg']}")
    print(f"   🚫 Blocs FR supprimés : {stats['removed_fr']}")
    print(f"   🚫 Blocs EN supprimés : {stats['removed_en']}")
    print(f"   🚫 Blocs Inconnus/Short : {stats['removed_unknown']}")
    print("=" * 70)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Phase 5 : Purification du corpus")
    parser.add_argument("--input", type=str, default="malagasy_lyrics_corpus.txt", help="Fichier brut")
    parser.add_argument("--output", type=str, default="malagasy_lyrics_cleaned.txt", help="Fichier propre")
    
    args = parser.parse_args()
    process_corpus(args.input, args.output)
