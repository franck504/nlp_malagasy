#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 4 : Fusion du Corpus
Regroupe tous les fichiers .txt individuels en un seul grand fichier texte
prêt pour l'entraînement d'un modèle NLP.
"""

import argparse
from pathlib import Path

def merge_corpus(output_dir="output", final_file="malagasy_lyrics_corpus.txt", raw_only=True):
    """
    Parcourt le dossier output et fusionne tous les fichiers texte.
    
    Args:
        output_dir: Dossier contenant les dossiers d'artistes.
        final_file: Nom du fichier final de sortie.
        raw_only: Si True, ne garde que les paroles (enlève Titre/Artiste/Source).
    """
    output_path = Path(output_dir)
    final_path = Path(final_file)

    if not output_path.exists():
        print(f"❌ Dossier {output_dir} introuvable !")
        return

    print("=" * 70)
    print("🚀 FUSION DU CORPUS")
    print(f"   Source : {output_path.resolve()}")
    print(f"   Destination : {final_path.resolve()}")
    print("=" * 70)

    count = 0
    with open(final_path, "w", encoding="utf-8") as outfile:
        # On parcourt les dossiers d'artistes (triés par nom)
        for artist_dir in sorted(output_path.iterdir()):
            if not artist_dir.is_dir():
                continue
            
            # On parcourt les fichiers .txt de l'artiste
            for txt_file in sorted(artist_dir.glob("*.txt")):
                try:
                    with open(txt_file, "r", encoding="utf-8") as infile:
                        content = infile.read()
                        
                        if raw_only:
                            # On sépare les paroles du header (séparé par ---)
                            parts = content.split("---", 1)
                            if len(parts) > 1:
                                lyrics = parts[1].strip()
                            else:
                                lyrics = content.strip()
                            
                            if lyrics:
                                outfile.write(lyrics + "\n\n")
                        else:
                            # On garde tout, incluant les métadonnées
                            outfile.write(content + "\n\n" + "="*30 + "\n\n")
                        
                        count += 1
                        if count % 500 == 0:
                            print(f"   🔄 {count} chansons traitées...")
                            
                except Exception as e:
                    print(f"   ⚠️ Erreur sur {txt_file.name} : {e}")

    print("=" * 70)
    print(f"✅ TERMINÉ !")
    print(f"   Total : {count} chansons fusionnées.")
    print(f"   Fichier créé : {final_file} ({final_path.stat().st_size / 1024 / 1024:.2f} MB)")
    print("=" * 70)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Phase 4 : Fusion du corpus Malagasy")
    parser.add_argument("--output", type=str, default="output", help="Dossier d'entrée (défaut: output)")
    parser.add_argument("--final", type=str, default="malagasy_lyrics_corpus.txt", help="Nom du fichier final")
    parser.add_argument("--metadata", action="store_true", help="Garder les métadonnées (Titre/Artiste) dans le fichier final")
    
    args = parser.parse_args()
    
    # Par défaut, on ne garde que les paroles pour le NLP (raw_only=True)
    merge_corpus(output_dir=args.output, final_file=args.final, raw_only=not args.metadata)
