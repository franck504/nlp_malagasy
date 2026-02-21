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

### Phase 2 : Scraper les paroles

```bash
# Tout scraper
python3 02_scrape_lyrics.py

# Un seul artiste
python3 02_scrape_lyrics.py --artist mahaleo

# Reprendre à partir de l'artiste #50
python3 02_scrape_lyrics.py --start-from 50
```

| Option            | Description                         | Défaut         |
|-------------------|--------------------------------------|----------------|
| `--artists-file`  | Fichier JSON des artistes            | `artists.json` |
| `--output`        | Dossier de sortie                    | `output/`      |
| `--delay`         | Délai entre requêtes (secondes)      | `2.0`          |
| `--start-from`    | Commencer à l'artiste N (0-indexé)   | `0`            |
| `--artist`        | Scraper un seul artiste (par slug)   | —              |

> 💡 Le mode **resume** est intégré : les chansons déjà téléchargées sont automatiquement ignorées.

### Phase 3 : Statistiques

```bash
python3 03_stats.py
```

## ☁️ Exécution sur Google Colab (Recommandé pour long runs)

Le scraping complet peut prendre plusieurs heures. Utiliser Google Colab avec Google Drive est la meilleure solution pour éviter de perdre les données.

### Méthode via Google Drive

1.  **ZIP** : Compressez le dossier `tononkira_rehetra` en ZIP.
2.  **Upload** : Uploadez le ZIP sur votre **Google Drive** et décompressez-le (ou uploadez le dossier directement).
3.  **Ouvrir** : Dans Google Colab, ouvrez le fichier [`Tononkira_Scraper_Colab.ipynb`](file:///mnt/01DB93AE0391F010/videos%202026/voambolana_malagasy/tononkira_rehetra/Tononkira_Scraper_Colab.ipynb).
4.  **Drive mount** : Exécutez la cellule de montage du Drive et naviguez vers le dossier avec `%cd`.
5.  **Lancer** : Suivez les étapes du notebook.

## 📁 Structure de sortie

```
tononkira_rehetra/
├── 01_discover_artists.py
├── 02_scrape_lyrics.py
├── 03_stats.py
├── README.md
├── artists.json               ← Phase 1
└── output/                    ← Phase 2
    ├── mahaleo/
    │   ├── ravorombazaha.txt
    │   ├── ry-tanindrazana.txt
    │   └── ...
    ├── ambondrona/
    │   ├── aza-adino.txt
    │   └── ...
    └── ...
```

### Format d'un fichier `.txt`

```
Titre: Ravorombazaha
Artiste: Mahaleo
Source: https://tononkira.serasera.org/hira/mahaleo/ravorombazaha
---
[paroles de la chanson]
```

## 🔄 Différences vs `from_tononkira_serasera/`

| Fonctionnalité         | Ancien scraper             | Ce projet                  |
|------------------------|----------------------------|----------------------------|
| Artistes               | 13 codés en dur            | Auto-découverte (~2 000+)  |
| Organisation           | Fichiers plats             | Dossier par artiste        |
| Métadonnées            | Non                        | Titre + Artiste + Source   |
| Resume                 | Non                        | Oui                        |
| CLI                    | Non                        | `--artist`, `--start-from` |
