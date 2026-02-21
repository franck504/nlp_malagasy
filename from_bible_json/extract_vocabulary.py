#!/usr/bin/env python3
"""
Script pour extraire tous les mots uniques des ressources bibliques en malgache.
Ce script lit tous les fichiers JSON de l'Ancien et du Nouveau Testament,
extrait les mots et crée un fichier de vocabulaire unique.
"""

import json
import re
from pathlib import Path
from typing import Set

def extract_words_from_text(text: str) -> Set[str]:
    """
    Extrait tous les mots d'un texte en malgache.
    Garde les formes avec apostrophes comme "fahalalan'ny".
    """
    # Remplacer les caractères unicode d'apostrophe par '
    text = text.replace('\u2019', "'")
    
    # Pattern pour extraire les mots (lettres + apostrophes internes)
    # Accepte les mots avec apostrophes comme "fahalalan'ny"
    pattern = r"[a-zA-ZàâäéèêëïîôùûüÀÂÄÉÈÊËÏÎÔÙÛÜ]+(?:'[a-zA-ZàâäéèêëïîôùûüÀÂÄÉÈÊËÏÎÔÙÛÜ]+)*"
    
    words = re.findall(pattern, text)
    
    # Convertir en minuscules et nettoyer
    cleaned_words = set()
    for word in words:
        # Enlever les apostrophes en début/fin si présentes
        word = word.strip("'")
        if word:  # Ignorer les mots vides
            # Garder la forme originale pour préserver la casse
            cleaned_words.add(word.lower())
    
    return cleaned_words


def extract_from_json_file(file_path: Path) -> Set[str]:
    """
    Extrait tous les mots d'un fichier JSON biblique.
    """
    words = set()
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Parcourir la structure JSON
        # Structure: {chapitre: {verset: texte}}
        for chapter_data in data.values():
            if isinstance(chapter_data, dict):
                for verse_text in chapter_data.values():
                    if isinstance(verse_text, str):
                        words.update(extract_words_from_text(verse_text))
    
    except Exception as e:
        print(f"Erreur lors de la lecture de {file_path}: {e}")
    
    return words


def main():
    """
    Fonction principale pour extraire le vocabulaire.
    """
    base_dir = Path(__file__).parent
    old_testament_dir = base_dir / "old_testament"
    new_testament_dir = base_dir / "new_testament"
    
    print("Extraction du vocabulaire malgache de la Bible...")
    print("=" * 60)
    
    all_words = set()
    
    # Traiter l'Ancien Testament
    print("\n📖 Traitement de l'Ancien Testament...")
    if old_testament_dir.exists():
        json_files = sorted(old_testament_dir.glob("*.json"))
        for json_file in json_files:
            print(f"  - {json_file.name}")
            words = extract_from_json_file(json_file)
            all_words.update(words)
    
    # Traiter le Nouveau Testament
    print("\n📖 Traitement du Nouveau Testament...")
    if new_testament_dir.exists():
        json_files = sorted(new_testament_dir.glob("*.json"))
        for json_file in json_files:
            print(f"  - {json_file.name}")
            words = extract_from_json_file(json_file)
            all_words.update(words)
    
    # Trier les mots par ordre alphabétique
    sorted_words = sorted(all_words)
    
    # Sauvegarder dans un fichier
    output_file = base_dir / "vocabulaire_malgache.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        for word in sorted_words:
            f.write(word + '\n')
    
    print("\n" + "=" * 60)
    print(f"✅ Extraction terminée !")
    print(f"📊 Nombre total de mots uniques : {len(sorted_words):,}")
    print(f"💾 Fichier de sortie : {output_file}")
    print("\n📝 Exemples de mots extraits :")
    for i, word in enumerate(sorted_words[:20], 1):
        print(f"  {i}. {word}")
    if len(sorted_words) > 20:
        print(f"  ... et {len(sorted_words) - 20:,} autres mots")


if __name__ == "__main__":
    main()
