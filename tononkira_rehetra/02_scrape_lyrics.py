#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 2 : Scraping des paroles de chansons depuis tononkira.serasera.org
Lit artists.json (généré par Phase 1) et télécharge toutes les paroles, 
organisées par dossier artiste avec un fichier .txt par chanson.
"""

import json
import re
import time
import argparse
import requests
import logging
from pathlib import Path
from urllib.parse import urlparse, parse_qs, unquote
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed


BASE_URL = "https://tononkira.serasera.org"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


# ============================================================
# HTTP
# ============================================================

def fetch_page(url, retries=3, delay=2):
    """Télécharge une page HTML avec retry et backoff exponentiel."""
    for attempt in range(1, retries + 1):
        try:
            r = requests.get(url, headers=HEADERS, timeout=20)
            r.raise_for_status()
            return r.text
        except requests.RequestException as e:
            print(f"    ⚠️  Tentative {attempt}/{retries} échouée : {e}")
            if attempt < retries:
                wait = delay * (2 ** (attempt - 1))
                time.sleep(wait)
    return None


# ============================================================
# PAGINATION
# ============================================================

def get_last_page_number(html):
    """Détecte le dernier numéro de page."""
    soup = BeautifulSoup(html, "html.parser")
    last_link = soup.find("a", attrs={"aria-label": "Farany"})
    if not last_link:
        return 1
    href = last_link.get("href", "")
    qs = parse_qs(urlparse(href).query)
    return int(qs.get("page", [1])[0])


# ============================================================
# EXTRACTION DES LIENS DE CHANSONS
# ============================================================

def extract_song_links(html):
    """Extrait les URLs des chansons depuis une page de liste artiste.
    
    Retourne une liste de tuples (url, titre_slug).
    """
    soup = BeautifulSoup(html, "html.parser")
    songs = []
    seen = set()

    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith(f"{BASE_URL}/hira/"):
            if href not in seen:
                seen.add(href)
                # Extraire le slug du titre depuis l'URL
                parts = href.replace(f"{BASE_URL}/hira/", "").split("/")
                titre_slug = parts[-1] if len(parts) >= 2 else parts[0]
                songs.append((href, titre_slug))

    return songs


# ============================================================
# EXTRACTION DES PAROLES
# ============================================================

def extract_song_info(html, song_url):
    """Extrait le titre, l'artiste et les paroles d'une page de chanson.
    
    Retourne un dict {title, artist, lyrics} ou None si échec.
    """
    soup = BeautifulSoup(html, "html.parser")

    # Titre — Le site utilise souvent <h2> pour "TITRE (Artiste)"
    title = ""
    title_elem = soup.find("h2") or soup.find("h1")
    if title_elem:
        title = title_elem.get_text(strip=True)
        # Nettoyer "TITRE (Artiste)" -> "TITRE"
        title = re.sub(r'\(.*?\)', '', title).strip()
    
    # Fallback sur le <title> HTML si tjours vide
    if not title and soup.title:
        title = soup.title.get_text().split("-")[0].strip()

    # Artiste — lien vers /mpihira/{slug}
    artist = ""
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/mpihira/" in href and "/hira" not in href and "/ankafizo" not in href:
            candidate = a.get_text(strip=True)
            if candidate and len(candidate) > 1:
                artist = candidate
                break

    # Paroles — div source puis siblings
    source_div = soup.find(
        "div",
        class_="print my-3 fst-italic",
        string=lambda x: x and "Nalaina tao amin'ny tononkira.serasera.org" in x
    )

    if not source_div:
        # Fallback : chercher un autre pattern
        source_div = soup.find(
            "div",
            string=lambda x: x and "tononkira.serasera.org" in str(x)
        )

    if not source_div:
        return None

    lines = []
    for elem in source_div.next_siblings:
        if getattr(elem, "name", None) in ["div", "h5", "form", "footer"]:
            break

        if isinstance(elem, str):
            t = elem.strip()
            if t:
                lines.append(t)
        elif elem.name == "br":
            lines.append("\n")
        else:
            t = elem.get_text(strip=True)
            if t:
                lines.append(t)

    lyrics = "\n".join(lines)
    # Nettoyer les sauts de ligne excessifs
    lyrics = re.sub(r"\n{3,}", "\n\n", lyrics).strip()

    if not lyrics:
        return None

    return {
        "title": title,
        "artist": artist,
        "lyrics": lyrics
    }


# ============================================================
# SAUVEGARDE
# ============================================================

def sanitize_filename(name):
    """Nettoie un nom pour l'utiliser comme nom de fichier."""
    # Remplacer les caractères interdits
    name = re.sub(r'[<>:"/\\|?*]', '', name)
    # Remplacer les espaces multiples
    name = re.sub(r'\s+', ' ', name).strip()
    # Limiter la longueur
    if len(name) > 200:
        name = name[:200]
    return name


def save_song(output_dir, titre_slug, song_info, song_url):
    """Sauvegarde une chanson dans un fichier .txt."""
    filename = sanitize_filename(titre_slug) + ".txt"
    filepath = output_dir / filename

    content = (
        f"Titre: {song_info['title']}\n"
        f"Artiste: {song_info['artist']}\n"
        f"Source: {song_url}\n"
        f"---\n"
        f"{song_info['lyrics']}\n"
    )

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    return filepath


# ============================================================
# SCRAPING D'UN ARTISTE
# ============================================================

def download_song_task(song_url, titre_slug, artist_dir, delay, logger):
    """Tâche individuelle de téléchargement d'une chanson pour multi-threading."""
    # Vérifier si déjà scrapé (resume)
    expected_file = artist_dir / (sanitize_filename(titre_slug) + ".txt")
    if expected_file.exists():
        return "skipped", expected_file.name

    html = fetch_page(song_url)
    if not html:
        return "failed", titre_slug

    song_info = extract_song_info(html, song_url)
    if not song_info or len(song_info["lyrics"]) < 50:
        return "too_short", titre_slug

    filepath = save_song(artist_dir, titre_slug, song_info, song_url)
    return "saved", filepath.name


def scrape_artist(artist_data, output_base, delay=2, logger=None, workers=1):
    """Scrape toutes les chansons d'un artiste en utilisant le multi-threading."""
    logger = logger or logging.getLogger(__name__)
    slug = artist_data["slug"]
    name = artist_data["name"]
    expected = artist_data["song_count"]

    artist_dir = output_base / slug
    artist_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"\n{'=' * 60}")
    logger.info(f"🎤 {name} (slug: {slug}, ~{expected} hira)")
    logger.info(f"{'=' * 60}")

    # Étape 1 : Découvrir toutes les chansons
    base_url = f"{BASE_URL}/mpihira/{slug}/hira"
    html = fetch_page(base_url)
    if not html:
        logger.error("  ❌ Impossible de charger la page artiste")
        return 0, 0, 1

    last_page = get_last_page_number(html)
    logger.info(f"  📄 {last_page} page(s) de chansons")

    all_songs = []
    for page in range(1, last_page + 1):
        page_url = f"{base_url}?page={page}"
        page_html = fetch_page(page_url)
        if page_html:
            songs = extract_song_links(page_html)
            all_songs.extend(songs)
        time.sleep(delay)

    # Dédupliquer
    seen_urls = set()
    unique_songs = []
    for url, titre in all_songs:
        if url not in seen_urls:
            seen_urls.add(url)
            unique_songs.append((url, titre))

    logger.info(f"  🎵 {len(unique_songs)} chansons trouvées (Mode: {workers} workers)")

    # Étape 2 : Scraper chaque chanson en parallèle
    saved = 0
    skipped = 0
    failed = 0

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(download_song_task, url, titre, artist_dir, delay, logger): (url, titre)
            for url, titre in unique_songs
        }

        for idx, future in enumerate(as_completed(futures), 1):
            try:
                status, info = future.result()
                if status == "saved":
                    logger.info(f"  [{idx}/{len(unique_songs)}] 💾 {info}")
                    saved += 1
                elif status == "skipped":
                    skipped += 1
                elif status == "failed":
                    logger.error(f"  [{idx}/{len(unique_songs)}] ❌ {info}")
                    failed += 1
                elif status == "too_short":
                    logger.warning(f"  [{idx}/{len(unique_songs)}] ⏭️ {info} (trop court)")
                    failed += 1
            except Exception as e:
                logger.error(f"  ❌ Erreur lors du téléchargement : {e}")
                failed += 1

    logger.info(f"\n  📊 Résultat : {saved} sauvées, {skipped} déjà existantes, {failed} échouées")
    return saved, skipped, failed


# ============================================================
# PIPELINE PRINCIPAL
# ============================================================

def run_scraping(artists_file="artists.json", output_dir="output",
                 delay=2.0, start_from=0, artist_slug=None, workers=1):
    """Pipeline principal : lit artists.json et scrape tout."""
    
    # Configuration du logging
    log_file = "scrape_lyrics.log"
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
    logger.info("🎵 PHASE 2 : SCRAPING DES PAROLES")
    logger.info(f"   Source : {artists_file}")
    logger.info(f"   Sortie : {output_dir}/")
    logger.info(f"   Mode   : {'Parallel (' + str(workers) + ' workers)' if workers > 1 else 'Sequential'}")
    logger.info("=" * 70)

    # Charger la liste des artistes
    artists_path = Path(artists_file)
    if not artists_path.exists():
        logger.error(f"\n❌ Fichier {artists_file} introuvable !")
        logger.info("💡 Exécutez d'abord : python3 01_discover_artists.py")
        return

    with open(artists_path, "r", encoding="utf-8") as f:
        artists = json.load(f)

    logger.info(f"\n📋 {len(artists)} artistes chargés")

    # Filtrer par artiste spécifique
    if artist_slug:
        artists = [a for a in artists if a["slug"] == artist_slug]
        if not artists:
            logger.error(f"\n❌ Artiste '{artist_slug}' non trouvé dans {artists_file}")
            return
        logger.info(f"🎯 Mode artiste unique : {artists[0]['name']}")

    # Appliquer start_from
    if start_from > 0:
        artists = artists[start_from:]
        logger.info(f"⏩ Démarrage à l'artiste #{start_from}")

    output_base = Path(output_dir)
    output_base.mkdir(parents=True, exist_ok=True)

    # Scraping
    total_saved = 0
    total_skipped = 0
    total_failed = 0

    for idx, artist in enumerate(artists):
        logger.info(f"\n{'━' * 70}")
        logger.info(f"  Progression : {idx + 1}/{len(artists)}")
        logger.info(f"{'━' * 70}")

        saved, skipped, failed = scrape_artist(artist, output_base, delay, logger, workers)
        total_saved += saved
        total_skipped += skipped
        total_failed += failed

    # Résumé final
    logger.info("\n" + "=" * 70)
    logger.info("📊 RÉSUMÉ FINAL")
    logger.info("=" * 70)
    logger.info(f"  Artistes traités   : {len(artists)}")
    logger.info(f"  Chansons sauvées   : {total_saved}")
    logger.info(f"  Chansons existantes: {total_skipped} (skipped)")
    logger.info(f"  Échecs             : {total_failed}")
    logger.info(f"  Dossier de sortie  : {output_base.resolve()}")
    logger.info(f"  Fichier log         : {log_file}")
    logger.info("=" * 70)
    logger.info("✅ Phase 2 terminée ! Lancez 03_stats.py pour voir les statistiques.")
    logger.info("=" * 70)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Phase 2 : Scraping des paroles depuis tononkira.serasera.org"
    )
    parser.add_argument(
        "--artists-file", type=str, default="artists.json",
        help="Fichier JSON des artistes (défaut: artists.json)"
    )
    parser.add_argument(
        "--output", type=str, default="output",
        help="Dossier de sortie (défaut: output/)"
    )
    parser.add_argument(
        "--delay", type=float, default=2.0,
        help="Délai entre les requêtes en secondes (défaut: 2.0)"
    )
    parser.add_argument(
        "--start-from", type=int, default=0,
        help="Commence à l'artiste N (0-indexé, défaut: 0)"
    )
    parser.add_argument(
        "--artist", type=str, default=None,
        help="Scraper un seul artiste par son slug (ex: mahaleo)"
    )
    parser.add_argument(
        "--workers", type=int, default=1,
        help="Nombre de threads pour le téléchargement parallèle (défaut: 1)"
    )
    args = parser.parse_args()

    run_scraping(
        artists_file=args.artists_file,
        output_dir=args.output,
        delay=args.delay,
        start_from=args.start_from,
        artist_slug=args.artist,
        workers=args.workers
    )
