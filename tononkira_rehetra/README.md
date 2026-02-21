# 🎵 Tononkira Rehetra — Scraper complet

Scraper pour collecter **toutes** les paroles de chansons malgaches depuis [tononkira.serasera.org](https://tononkira.serasera.org/), organisées par dossier artiste.

## 📋 Prérequis

```bash
pip install requests beautifulsoup4
```

## 🚀 Usage Local

### Phase 1 : Découvrir tous les artistes

```bash
python3 01_discover_artists.py
```

→ Génère `artists.json` avec ~2 000 artistes et leur nombre de chansons.

| Option      | Description                        | Défaut        |
|-------------|-------------------------------------|---------------|
| `--delay`   | Délai entre requêtes (secondes)     | `2.0`         |
| `--output`  | Fichier JSON de sortie              | `artists.json`|

### Phase 2 : Scraper les paroles (Turbo)

```bash
# Tout scraper à haute vitesse (recommandé sur Colab)
python3 02_scrape_lyrics.py --delay 0.5 --artist-workers 4 --song-workers 10
```

| Option            | Description                         | Défaut         |
|-------------------|--------------------------------------|----------------|
| `--artists-file`  | Fichier JSON des artistes            | `artists.json` |
| `--output`        | Dossier de sortie                    | `output/`      |
| `--delay`         | Délai entre requêtes (secondes)      | `1.0`          |
| `--artist-workers`| Nombre d'artistes en parallèle (TP)  | `1`            |
| `--song-workers`  | Nombre de chansons en parallèle (TP) | `5`            |
| `--start-from`    | Commencer à l'artiste N (0-indexé)   | `0`            |
| `--artist`        | Scraper un seul artiste (par slug)   | —              |

### Phase 3 : Statistiques

```bash
python3 03_stats.py
```

### Phase 4 : Fusion du Corpus

```bash
# Fusionne tous les fichiers .txt en un seul gros corpus brut
python3 04_merge_corpus.py
```

### Phase 5 : Purification (Nettoyage NLP)

```bash
# Filtre les phrases non-malgaches et nettoie le texte
python3 05_clean_corpus.py --input malagasy_lyrics_corpus.txt --output malagasy_lyrics_cleaned.txt
```

---

## ☁️ Exécution sur Google Colab

Le notebook [`Voambolana_Malagasy_Main.ipynb`](file:///mnt/01DB93AE0391F010/videos%202026/voambolana_malagasy/Voambolana_Malagasy_Main.ipynb) est le centre de commande pour exécuter ces étapes sur le cloud et sauvegarder sur Google Drive.

## 📁 Structure de sortie finalisée

```
tononkira_rehetra/
├── artists.json                # Liste des artistes (Phase 1)
├── output/                     # Dossiers par artiste (Phase 2)
├── malagasy_lyrics_corpus.txt  # Corpus brut (Phase 4)
└── malagasy_lyrics_cleaned.txt # Corpus propre (Phase 5) ✨
```

---
**NLP Malagasy Foundation Phase** 🇲🇬🚀
