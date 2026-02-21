# 📚 Vocabulaire Malgache - Module Web Scraping

Module d'enrichissement du vocabulaire malgache par scraping web et fusion avec le vocabulaire biblique.

## 📊 Résultat Final

**23,617 mots malgaches uniques** répartis comme suit :
- **Bible** : 21,346 mots (90.4%)
- **Web** : 2,271 mots (9.6%)

## 📁 Structure

```
from_scrapping_magazine_web/
│
├── 📜 Scripts (3 fichiers)
│   ├── 0_extract_from_web.py              # Extraction depuis raw_texts
│   ├── 3_filtre_vocabulaire.py            # Filtrage français→malgache
│   └── 4_merge_bible_web.py               # Fusion Bible+Web
│
├── 📊 Résultats (3 fichiers)
│   ├── 1_vocabulaire_web_brut.txt         # 2,952 mots (brut)
│   ├── 2_vocabulaire_web_filtre.txt       # 2,271 mots (filtré)
│   └── 5_vocabulaire_malgache_TOTAL.txt ⭐ # 23,617 mots (FINAL)
│
└── 📂 Données
    └── raw_texts/                          # 68 fichiers scrapés
```

## 🚀 Workflow

### Workflow Complet (3 étapes)

#### ÉTAPE 0 : Extraction (optionnel)
Extrait le vocabulaire depuis les fichiers raw_texts
```bash
python3 0_extract_from_web.py
```
**Sortie** : `1_vocabulaire_web_brut.txt` (2,952 mots)

#### ÉTAPE 1 : Filtrage ⭐
Supprime les mots français pour ne garder que le malgache
```bash
python3 3_filtre_vocabulaire.py
```
**Entrée** : `1_vocabulaire_web_brut.txt`  
**Sortie** : `2_vocabulaire_web_filtre.txt` (2,271 mots)  
**Exclusions** : 681 mots français (23.1%)

#### ÉTAPE 2 : Fusion ⭐
Fusionne le vocabulaire biblique avec le vocabulaire web
```bash
python3 4_merge_bible_web.py
```
**Entrée** : Bible (21,346) + Web (2,271)  
**Sortie** : `5_vocabulaire_malgache_TOTAL.txt` (23,617 mots)

## 📝 Fichiers de Sortie

| Fichier | Contenu | Mots | Description |
|---------|---------|------|-------------|
| `1_vocabulaire_web_brut.txt` | Brut | 2,952 | Nouveaux mots vs Bible |
| `2_vocabulaire_web_filtre.txt` | Filtré | 2,271 | Sans mots français |
| `5_vocabulaire_malgache_TOTAL.txt` ⭐ | Final | 23,617 | Bible + Web |

## 📂 Sources de Données

### raw_texts/ (68 fichiers)
Textes scrapés depuis des sites officiels malgaches :
- **presidence.gov.mg** - Site de la Présidence
- **primature.gov.mg** - Site de la Primature
- Autres sites gouvernementaux malgaches

**Langue** : Malgache (filtré automatiquement)  
**Format** : Fichiers texte (.txt)

## 🔧 Scripts Détaillés

### 0_extract_from_web.py
**Fonction** : Extraction du vocabulaire depuis raw_texts  
**Utilisation** :
```bash
python3 0_extract_from_web.py
```
**Process** :
1. Lit tous les fichiers de `raw_texts/`
2. Extrait les mots malgaches uniques
3. Compare avec le vocabulaire biblique
4. Sauvegarde les nouveaux mots dans `1_vocabulaire_web_brut.txt`

### 3_filtre_vocabulaire.py
**Fonction** : Filtrage français → malgache  
**Utilisation** :
```bash
python3 3_filtre_vocabulaire.py [--input FILE] [--output FILE] [--no-backup]
```
**Filtres appliqués** :
- Liste de 500+ mots français
- Terminaisons françaises (-tion, -ment, -ance, etc.)
- Accents français (é, è, à, etc.)
- Mots trop courts (< 3 lettres)

### 4_merge_bible_web.py
**Fonction** : Fusion Bible + Web  
**Utilisation** :
```bash
python3 4_merge_bible_web.py
```
**Process** :
1. Charge vocabulaire Bible
2. Charge vocabulaire Web filtré
3. Fusionne (union des ensembles)
4. Sauvegarde dans `5_vocabulaire_malgache_TOTAL.txt`

## 📈 Statistiques de Filtrage

### Mots Exclus (681 au total)
- **Liste française** : 395 mots (58%)
- **Accents français** : 165 mots (24%)
- **Terminaisons françaises** : 100 mots (15%)
- **Trop courts** : 21 mots (3%)

### Exemples de Mots Exclus
- Français évidents : accord, administration, général, etc.
- Terminaisons : accouchement, financement, etc.
- Accents : académie, actualités, etc.

### Exemples de Mots Conservés
- Mots administratifs : minisiteran, praiminisitra, fiadidiana
- Lieux : iavoloha, ambohitsorohitra, toliara
- Noms propres malgaches : andriamatoa, etc.

## ✅ Pour Git

### Fichiers Inclus
- ✅ Scripts Python (3 fichiers)
- ✅ Fichiers résultats (3 fichiers .txt)
- ✅ raw_texts/ (68 fichiers sources)
- ✅ Documentation (README.txt, README.md)
- ✅ .gitignore

### Fichiers Ignorés (.gitignore)
- ❌ `_archive/` - Anciens scripts
- ❌ `*_backup.txt` - Backups
- ❌ `*_test.txt` - Fichiers de test
- ❌ Fichiers temporaires

## 🎯 Utilisation du Vocabulaire Final

Le fichier `5_vocabulaire_malgache_TOTAL.txt` peut être utilisé pour :
- 🔤 **Autocomplétion** de texte en malgache
- ✍️ **Correction orthographique** malgache
- 📖 **Dictionnaire** malgache
- 🔍 **Recherche** et indexation de texte malgache

## 📅 Informations

- **Date de création** : 2024-12-25
- **Auteur** : Franck
- **Projet** : Voambolana Malagasy - Enrichissement Vocabulaire
- **Licence** : À définir

---

**Vocabulaire total** : **23,617 mots malgaches uniques** ✨
