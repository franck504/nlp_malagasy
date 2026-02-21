#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 1 : Découverte automatique de tous les artistes sur tononkira.serasera.org
Parcourt toutes les pages de la liste des artistes et sauvegarde dans artists.json
"""

import json
import re
import time
import argparse
import requests
import logging
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup


BASE_URL = "https://tononkira.serasera.org"
ARTISTS_LIST_URL = f"{BASE_URL}/mpihira"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def fetch_page(url, retries=3, delay=2):
    """Télécharge une page HTML avec retry et backoff exponentiel."""
    for attempt in range(1, retries + 1):
        try:
            r = requests.get(url, headers=HEADERS, timeout=20)
            r.raise_for_status()
            return r.text
        except requests.RequestException as e:
            print(f"  ⚠️  Tentative {attempt}/{retries} échouée pour {url} : {e}")
            if attempt < retries:
                wait = delay * (2 ** (attempt - 1))
                print(f"      Attente {wait}s avant retry...")
                time.sleep(wait)
    print(f"  ❌ Échec définitif : {url}")
    return None


def get_last_page_number(html):
    """Détecte le dernier numéro de page depuis le lien 'Farany'."""
    soup = BeautifulSoup(html, "html.parser")
    last_link = soup.find("a", attrs={"aria-label": "Farany"})
    if not last_link:
        return 1
    href = last_link.get("href", "")
    qs = parse_qs(urlparse(href).query)
    return int(qs.get("page", [1])[0])


def extract_artists_from_page(html):
    """Extrait les artistes d'une page de liste.
    
    Retourne une liste de dicts : {name, slug, song_count}
    """
    soup = BeautifulSoup(html, "html.parser")
    artists = []

    # Chaque artiste est un lien vers /mpihira/{slug}
    # suivi d'un lien "Misy hira N" vers /mpihira/{slug}/hira
    for link in soup.find_all("a", href=True):
        href = link["href"]

        # On cherche les liens artiste de la forme /mpihira/{slug}
        # mais PAS /mpihira/{slug}/hira ni /mpihira/{slug}/ankafizo
        if not href.startswith(f"{BASE_URL}/mpihira/"):
            continue

        path = href.replace(f"{BASE_URL}/mpihira/", "")
        # Ignorer les sous-pages (hira, ankafizo)
        if "/" in path or not path:
            continue

        slug = path
        name = link.get_text(strip=True)

        if not name or not slug:
            continue

        # Chercher le nombre de chansons dans le frère suivant
        song_count = 0
        next_sibling = link.find_next("a", href=True)
        if next_sibling:
            text = next_sibling.get_text(strip=True)
            match = re.search(r"Misy hira (\d+)", text)
            if match:
                song_count = int(match.group(1))

        artists.append({
            "name": name,
            "slug": slug,
            "song_count": song_count
        })

    return artists


def discover_all_artists(delay=2, output_file="artists.json"):
    """Pipeline complet : parcourt toutes les pages et sauvegarde artists.json."""
    
    # Configuration du logging
    log_file = "discover_artists.log"
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger(__name__)

    logger.info("=" * 70)
    logger.info("🔍 PHASE 1 : DÉCOUVERTE DE TOUS LES ARTISTES")
    logger.info(f"   Source : {ARTISTS_LIST_URL}")
    logger.info("=" * 70)

    # Étape 1 : Détecter le nombre de pages
    logger.info("\n📄 Détection du nombre de pages...")
    first_page = fetch_page(ARTISTS_LIST_URL)
    if not first_page:
        logger.error("❌ Impossible de charger la première page !")
        return

    last_page = get_last_page_number(first_page)
    logger.info(f"   → {last_page} pages détectées")

    # Étape 2 : Parcourir toutes les pages
    all_artists = []
    seen_slugs = set()

    for page_num in range(1, last_page + 1):
        url = f"{ARTISTS_LIST_URL}?page={page_num}"
        logger.info(f"📥 Page {page_num}/{last_page} ...")

        html = fetch_page(url)
        if not html:
            continue

        page_artists = extract_artists_from_page(html)

        # Dédupliquer
        new_count = 0
        for artist in page_artists:
            if artist["slug"] not in seen_slugs:
                seen_slugs.add(artist["slug"])
                all_artists.append(artist)
                new_count += 1

        logger.info(f"  → {new_count} nouveaux artistes")
        time.sleep(delay)

    # Étape 3 : Filtrer les artistes sans chansons
    artists_with_songs = [a for a in all_artists if a["song_count"] > 0]
    artists_no_songs = len(all_artists) - len(artists_with_songs)

    # Étape 4 : Sauvegarder
    output_path = Path(output_file)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(artists_with_songs, f, ensure_ascii=False, indent=2)

    # Résumé
    total_songs = sum(a["song_count"] for a in artists_with_songs)
    top_artists = sorted(artists_with_songs, key=lambda a: a["song_count"], reverse=True)

    logger.info("\n" + "=" * 70)
    logger.info("📊 RÉSUMÉ")
    logger.info("=" * 70)
    logger.info(f"  Artistes trouvés    : {len(all_artists)}")
    logger.info(f"  Artistes avec hira  : {len(artists_with_songs)}")
    logger.info(f"  Artistes sans hira  : {artists_no_songs} (exclus)")
    logger.info(f"  Total chansons      : {total_songs:,}")
    logger.info(f"  Fichier sauvegardé  : {output_path}")
    logger.info(f"  Fichier log         : {log_file}")

    logger.info(f"\n🏆 Top 15 artistes :")
    for i, a in enumerate(top_artists[:15], 1):
        logger.info(f"  {i:3d}. {a['name']:40s} ({a['song_count']:4d} hira)")

    logger.info("=" * 70)
    logger.info("✅ Phase 1 terminée ! Lancez maintenant 02_scrape_lyrics.py")
    logger.info("=" * 70)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Phase 1 : Découverte de tous les artistes sur tononkira.serasera.org"
    )
    parser.add_argument(
        "--delay", type=float, default=2.0,
        help="Délai entre les requêtes en secondes (défaut: 2.0)"
    )
    parser.add_argument(
        "--output", type=str, default="artists.json",
        help="Fichier de sortie JSON (défaut: artists.json)"
    )
    args = parser.parse_args()

    discover_all_artists(delay=args.delay, output_file=args.output)
