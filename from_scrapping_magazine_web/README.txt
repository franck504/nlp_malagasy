╔══════════════════════════════════════════════════════════════╗
║             VOCABULAIRE MALGACHE - Module Web                ║
╚══════════════════════════════════════════════════════════════╝

📁 STRUCTURE DU DOSSIER
═══════════════════════════════════════════════════════════════

├── 0_extract_from_web.py           Extraction depuis raw_texts
├── 1_vocabulaire_web_brut.txt      2,952 mots (brut)
├── 2_vocabulaire_web_filtre.txt    2,271 mots (filtré)
├── 3_filtre_vocabulaire.py         Script de filtrage
├── 4_merge_bible_web.py            Script de fusion Bible+Web
├── 5_vocabulaire_malgache_TOTAL.txt ⭐ 23,617 mots (FINAL)
└── raw_texts/                      68 fichiers texte scrapés

═══════════════════════════════════════════════════════════════

🚀 WORKFLOW COMPLET
═══════════════════════════════════════════════════════════════

ÉTAPE 0 (optionnel) : Extraction depuis raw_texts
    python3 0_extract_from_web.py
    → Crée 1_vocabulaire_web_brut.txt

ÉTAPE 1 : Filtrage (supprimer mots français)
    python3 3_filtre_vocabulaire.py
    → Lit  : 1_vocabulaire_web_brut.txt
    → Crée : 2_vocabulaire_web_filtre.txt

ÉTAPE 2 : Fusion Bible + Web
    python3 4_merge_bible_web.py
    → Lit  : Bible + 2_vocabulaire_web_filtre.txt
    → Crée : 5_vocabulaire_malgache_TOTAL.txt

═══════════════════════════════════════════════════════════════

📊 STATISTIQUES
═══════════════════════════════════════════════════════════════

Bible           : 21,346 mots (90.4%)
Web (filtré)    :  2,271 mots ( 9.6%)
────────────────────────────────────
TOTAL           : 23,617 mots (100%)

═══════════════════════════════════════════════════════════════

📝 FICHIERS IMPORTANTS
═══════════════════════════════════════════════════════════════

⭐ 5_vocabulaire_malgache_TOTAL.txt
   → Vocabulaire complet final (Bible + Web)
   → 23,617 mots malgaches uniques
   → Prêt à utiliser pour autocorrection

📂 raw_texts/
   → 68 fichiers texte scrapés depuis sites malgaches
   → Sources : presidence.gov.mg, primature.gov.mg, etc.

═══════════════════════════════════════════════════════════════

🔧 SCRIPTS
═══════════════════════════════════════════════════════════════

0_extract_from_web.py
   Extrait vocabulaire depuis raw_texts/ (vs Bible)

3_filtre_vocabulaire.py
   Filtre mots français → malgache
   
4_merge_bible_web.py
   Fusionne Bible + Web

═══════════════════════════════════════════════════════════════

✅ PRÊT POUR GIT
═══════════════════════════════════════════════════════════════

Fichiers à inclure :
  ✓ Scripts Python (3 fichiers)
  ✓ Fichiers .txt de résultats (3 fichiers)
  ✓ raw_texts/ (68 fichiers)
  ✓ README.txt et README.md

Fichiers ignorés (.gitignore) :
  ✗ _archive/
  ✗ Fichiers backup et test

═══════════════════════════════════════════════════════════════
Date : 2024-12-25
Auteur : Franck
Projet : Voambolana Malagasy - Enrichissement Vocabulaire
═══════════════════════════════════════════════════════════════
