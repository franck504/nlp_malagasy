#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script amélioré pour filtrer les noms de personnes du vocabulaire malgache.
Utilise une approche multi-critères pour améliorer la précision.
"""

import json
import re
from pathlib import Path
from collections import defaultdict, Counter

def analyze_word_contexts(json_dir):
    """
    Analyse le contexte d'apparition de chaque mot dans les textes bibliques.
    Retourne:
    - word_total_count: nombre total d'occurrences pour chaque mot
    - word_with_marker_count: nombre d'occurrences avec marqueur de nom
    - word_contexts: exemples de contextes pour chaque mot
    """
    word_total_count = Counter()
    word_with_marker_count = Counter()
    word_contexts = defaultdict(list)
    
    # Marqueurs de noms propres
    name_patterns = [
        r'\bi\s+(\w+)',
        r'\ban\'i\s+(\w+)',
        r'\bzanak\'i\s+(\w+)',
        r'\btamin\'i\s+(\w+)',
        r'\bamin\'i\s+(\w+)',
    ]
    
    combined_pattern = '|'.join(f'({p})' for p in name_patterns)
    
    for testament_dir in ['old_testament', 'new_testament']:
        testament_path = json_dir / testament_dir
        if not testament_path.exists():
            continue
            
        for json_file in testament_path.glob('*.json'):
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for chapter_num, verses in data.items():
                for verse_num, text in verses.items():
                    # S'assurer que le texte est une chaîne
                    text = str(text)
                    # Compter tous les mots
                    words = re.findall(r"[a-zA-ZàâäéèêëïîôùûüÀÂÄÉÈÊËÏÎÔÙÛÜ]+(?:'[a-zA-ZàâäéèêëïîôùûüÀÂÄÉÈÊËÏÎÔÙÛÜ]+)*", text.lower())
                    for word in words:
                        word_total_count[word] += 1
                    
                    # Trouver les mots avec marqueurs
                    for match in re.finditer(combined_pattern, text, re.IGNORECASE):
                        for i, group in enumerate(match.groups()):
                            if group and i % 2 == 1:  # Les groupes impairs contiennent les mots capturés
                                word = group.lower()
                                word_with_marker_count[word] += 1
                                # Garder quelques exemples de contexte
                                if len(word_contexts[word]) < 3:
                                    start = max(0, match.start() - 30)
                                    end = min(len(text), match.end() + 30)
                                    context = text[start:end].strip()
                                    word_contexts[word].append(context)
    
    return word_total_count, word_with_marker_count, word_contexts

def load_common_words_whitelist():
    """
    Liste de mots malgaches très courants qui ne sont jamais des noms propres.
    """
    return {
        # Pronoms et déterminants
        'aho', 'ianao', 'izy', 'izahay', 'isika', 'ianareo', 'izy', 'ireo',
        'ity', 'io', 'ilay', 'ireny', 'izany', 'izao', 'ny',
        
        # Mots très fréquents (de la liste fournie par l'utilisateur)
        'aetriny', 'aetry', 'afaho', 'afaka', 'afatory', 'afindrao', 'afeno',
        'ahazoana', 'ahiana', 'ahoana', 'ahontsankontsany', 'ahoroko', 'aina',
        'akaiky', 'akana', 'akanjo', 'akany', 'akora', 'alainao', 'alainy',
        'alaivo', 'alefaso', 'aleoko', 'aleontsika', 'aleveno', 'alika',
        'alinalina', 'alona', 'ambakainy', 'ambarao', 'amboariny', 'amboary',
        'ambony', 'ampahafantariny', 'ampahafantaro', 'ampahafolon', 'ampahany',
        'ampaherezo', 'ampakariko', 'ampiakariny', 'ampianaro', 'ampiarahina',
        'ampiaraho', 'ampiasao', 'ampingan', 'ampio', 'ampiomano', 'ampirisihinay',
        'ampisotroy', 'ampitomboiny', 'ampitomboy', 'ampongabendanitra',
        'anamparan', 'anarana', 'anareo', 'anaro', 'andao', 'andeha', 'andevon',
        'andrahoy', 'andraikiny', 'andraikitr', 'zato', 'zavatra', 'zavona',
        
        # Mots courants additionnels
        'dia', 'fa', 'ka', 'koa', 'ary', 'na', 'sy', 'no', 'any', 'eto',
        'tao', 'teo', 'amin', 'ho', 'tsy', 'tonga', 'manao', 'hoy',
        'rehefa', 'raha', 'satria', 'nefa', 'kanefa', 'izay', 'izao',
        'marina', 'tokoa', 'indrindra', 'mihitsy', 'foana', 'mandrakariva',
        'andro', 'alina', 'maraina', 'hariva', 'tany', 'lanitra',
        'olona', 'lehilahy', 'vehivavy', 'zaza', 'ray', 'reny',
        'zanaka', 'rahalahy', 'anabavy', 'havana',
    }

def identify_proper_names(json_dir, vocab_file):
    """
    Identifie les noms propres en utilisant plusieurs critères.
    """
    print("🔍 Analyse approfondie des mots...")
    print("=" * 60)
    
    # Analyser les contextes
    word_total, word_with_marker, word_contexts = analyze_word_contexts(json_dir)
    
    # Charger la liste blanche
    whitelist = load_common_words_whitelist()
    
    # Critères pour identifier un nom propre
    proper_names = set()
    statistics = {
        'exclusivity_high': 0,  # >80% avec marqueur
        'exclusivity_medium': 0,  # 50-80% avec marqueur
        'frequency_based': 0,  # Rare + toujours avec marqueur
        'whitelisted': 0,  # Dans la liste blanche
    }
    
    for word, marker_count in word_with_marker.items():
        total_count = word_total[word]
        exclusivity_ratio = marker_count / total_count if total_count > 0 else 0
        
        # Ignorer les mots de la liste blanche
        if word in whitelist:
            statistics['whitelisted'] += 1
            continue
        
        # Ignorer les mots très courts (probablement grammaticaux)
        if len(word) <= 2:
            continue
        
        # Critère 1: Exclusivité très élevée (>80% avec marqueur)
        # Ces mots apparaissent presque toujours avec un marqueur
        if exclusivity_ratio > 0.8 and total_count >= 3:
            proper_names.add(word)
            statistics['exclusivity_high'] += 1
            continue
        
        # Critère 2: Exclusivité moyenne + faible fréquence
        # Mots qui apparaissent souvent avec marqueur ET sont rares
        if exclusivity_ratio > 0.5 and total_count <= 20:
            proper_names.add(word)
            statistics['exclusivity_medium'] += 1
            continue
        
        # Critère 3: Exclusivité parfaite pour mots peu fréquents
        # Mots qui apparaissent UNIQUEMENT avec marqueur
        if exclusivity_ratio == 1.0 and total_count >= 2 and total_count <= 50:
            proper_names.add(word)
            statistics['frequency_based'] += 1
            continue
    
    print(f"\n📊 Statistiques de détection:")
    print(f"  - Exclusivité élevée (>80%): {statistics['exclusivity_high']}")
    print(f"  - Exclusivité moyenne (50-80%) + rare: {statistics['exclusivity_medium']}")
    print(f"  - Exclusivité parfaite + peu fréquent: {statistics['frequency_based']}")
    print(f"  - Mots protégés (liste blanche): {statistics['whitelisted']}")
    print(f"  - Total noms détectés: {len(proper_names)}")
    
    return proper_names, word_total, word_with_marker

def create_filtered_vocabulary(vocab_file, proper_names, output_dir):
    """
    Crée les fichiers de sortie: noms propres et vocabulaire filtré.
    """
    # Charger le vocabulaire complet
    with open(vocab_file, 'r', encoding='utf-8') as f:
        all_words = set(line.strip() for line in f if line.strip())
    
    # Séparer noms propres et vocabulaire commun
    proper_names_lower = {name.lower() for name in proper_names}
    common_vocabulary = sorted(all_words - proper_names_lower)
    proper_names_sorted = sorted(proper_names_lower)
    
    # Écrire les fichiers
    names_file = output_dir / 'noms_propres_malgaches_v2.txt'
    vocab_file_out = output_dir / 'vocabulaire_malgache_sans_noms_v2.txt'
    
    with open(names_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(proper_names_sorted))
    
    with open(vocab_file_out, 'w', encoding='utf-8') as f:
        f.write('\n'.join(common_vocabulary))
    
    print(f"\n✅ Filtrage amélioré terminé !")
    print(f"📊 Résultats:")
    print(f"  - Vocabulaire original : {len(all_words):,} mots")
    print(f"  - Noms propres détectés : {len(proper_names_sorted):,} noms")
    print(f"  - Vocabulaire filtré : {len(common_vocabulary):,} mots")
    print(f"  - Pourcentage filtré : {len(proper_names_sorted)/len(all_words)*100:.1f}%")
    
    print(f"\n💾 Fichiers créés :")
    print(f"  - {names_file}")
    print(f"  - {vocab_file_out}")
    
    return proper_names_sorted, common_vocabulary

def main():
    # Chemins
    base_dir = Path(__file__).parent
    vocab_file = base_dir / 'vocabulaire_malgache.txt'
    
    # Identifier les noms propres avec la méthode améliorée
    proper_names, word_total, word_with_marker = identify_proper_names(base_dir, vocab_file)
    
    # Créer les fichiers filtrés
    proper_names_sorted, common_vocabulary = create_filtered_vocabulary(
        vocab_file, proper_names, base_dir
    )
    
    # Afficher quelques exemples
    print(f"\n📝 Exemples de noms propres détectés (10 premiers):")
    for i, name in enumerate(proper_names_sorted[:10], 1):
        total = word_total[name]
        with_marker = word_with_marker[name]
        ratio = with_marker / total * 100 if total > 0 else 0
        print(f"  {i}. {name} (total: {total}, avec marqueur: {with_marker}, ratio: {ratio:.1f}%)")
    
    print(f"\n📝 Exemples de mots communs conservés (10 premiers avec 'a'):")
    common_with_a = [w for w in common_vocabulary if w.startswith('a')][:10]
    for i, word in enumerate(common_with_a, 1):
        total = word_total.get(word, 0)
        with_marker = word_with_marker.get(word, 0)
        ratio = with_marker / total * 100 if total > 0 else 0
        print(f"  {i}. {word} (total: {total}, avec marqueur: {with_marker}, ratio: {ratio:.1f}%)")

if __name__ == "__main__":
    main()
