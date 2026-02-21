# 🎵 Vocabulaire Malgache - Paroles de Chansons (Tononkira)

Module d'extraction du vocabulaire depuis les paroles de chansons malgaches du site **tononkira.serasera.org**.

## 📊 Source

- **Site** : https://tononkira.serasera.org
- **Type** : Paroles de chansons malgaches
- **Artistes scrapés** : 13 artistes (Mahaleo, Ambondrona, Rebika, Poopy, Bodo, etc.)
- **Nombre de chansons** : 877 chansons

## 🚀 Workflow

### ☁️ Sur Google Colab

#### 1. Scraping des paroles
```python
# Dans Google Colab
!pip install beautifulsoup4 requests

# Copier le contenu de scraper.py
# Exécuter le scraping
python scraper.py
```

#### 2. Télécharger les fichiers
```python
# Dans Google Colab
# Copier le contenu de download_from_colab.py
# Télécharger l'archive ZIP
python download_from_colab.py
```

### 💻 En Local

#### 3. Extraction du vocabulaire
```bash
python3 0_extract_from_lyrics.py
```
**Sortie** : `1_vocabulaire_lyrics_brut.txt`

#### 4. Filtrage français → malgache
```bash
python3 3_filtre_vocabulaire.py --input 1_vocabulaire_lyrics_brut.txt --output 2_vocabulaire_lyrics_filtre.txt
```
**Sortie** : `2_vocabulaire_lyrics_filtre.txt`

#### 5. Fusion avec Bible + Web
```bash
python3 4_merge_all.py
```
**Sortie** : `5_vocabulaire_malgache_COMPLET.txt` ⭐

## 📁 Structure

```
from_tononkira_serasera/
├── scraper.py                          # Scraping (Google Colab)
├── download_from_colab.py              # Download depuis Colab
├── 0_extract_from_lyrics.py            # Extraction vocabulaire
├── 3_filtre_vocabulaire.py             # Filtrage
├── 4_merge_all.py                      # Fusion TOUT
├── tononkira_raw_texts/                # 877 fichiers de paroles ⭐
├── 1_vocabulaire_lyrics_brut.txt       # Vocabulaire brut
├── 2_vocabulaire_lyrics_filtre.txt     # Vocabulaire filtré
└── 5_vocabulaire_malgache_COMPLET.txt  # FINAL COMPLET ⭐
```

## 🎯 Résultat Final

Le fichier `5_vocabulaire_malgache_COMPLET.txt` contient **TOUS** les mots malgaches de 3 sources :
- ✅ Bible (21,346 mots)
- ✅ Web (2,163 mots)
- ✅ Paroles de chansons (nouveaux mots)

## 📝 Notes

- Les paroles de chansons apportent du vocabulaire **moderne** et **familier**
- Complément parfait à la Bible (vocabulaire religieux) et au Web (vocabulaire administratif)
- 877 chansons analysées de 13 artistes malgaches populaires

## 🎤 Artistes Scrapés

1. Mahaleo (230 chansons)
2. Henri Ratsimbazafy (103 chansons)
3. Poopy (132 chansons)
4. Bodo (90 chansons)
5. Rebika (79 chansons)
6. Ambondrona (70 chansons)
7. Bessa sy Lola (67 chansons)
8. Lola Lahy (20 chansons)
9. Farakely (20 chansons)
10. Voahangy (19 chansons)
11. Vola sy Noro (20 chansons)
12. Levelo (16 chansons)
13. Zandry Gasy (14 chansons)

---

**Vocabulaire enrichi avec des paroles de chansons malgaches** 🎵
