import os
import json
import argparse

def consolidate_corpus(lyrics_path, bible_dir, wiki_path, output_path, deduplicate=True):
    print("======================================================================")
    print("📚 CONSOLIDATION DU CORPUS FINAL (Lyrics + Bible + Wikipedia)")
    print(f"   Lyrics       : {lyrics_path}")
    print(f"   Bible        : {bible_dir}")
    print(f"   Wikipedia    : {wiki_path}")
    print(f"   Sortie       : {output_path}")
    print(f"   Dédoublonage : {'OUI' if deduplicate else 'NON'}")
    print("======================================================================")

    total_blocks = 0
    seen_blocks = set() if deduplicate else None
    
    with open(output_path, 'w', encoding='utf-8') as f_out:
        # 1. Charger les Lyrics nettoyés
        if os.path.exists(lyrics_path):
            print("📖 Chargement des lyrics nettoyés...")
            with open(lyrics_path, 'r', encoding='utf-8') as f_in:
                content = f_in.read()
                blocks = content.split("\n\n")
                added = 0
                for block in blocks:
                    clean_b = block.strip()
                    if not clean_b: continue
                    if deduplicate:
                        if clean_b in seen_blocks: continue
                        seen_blocks.add(clean_b)
                    f_out.write(clean_b + "\n\n")
                    added += 1
                    total_blocks += 1
            print(f"   ✅ {added} blocs de lyrics uniques ajoutés.")

        # 2. Charger la Bible
        bible_blocks = 0
        print("📖 Chargement de la Bible...")
        for root_dir in ['old_testament', 'new_testament']:
            full_bible_path = os.path.join(bible_dir, root_dir)
            if not os.path.exists(full_bible_path): continue
            for filename in sorted(os.listdir(full_bible_path)):
                if filename.endswith('.json'):
                    file_path = os.path.join(full_bible_path, filename)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f_json:
                            data = json.load(f_json)
                            for key, chapter in data.items():
                                if key == "meta" or not isinstance(chapter, dict): continue
                                for v_key, verse_text in chapter.items():
                                    if isinstance(verse_text, str):
                                        clean_text = verse_text.strip()
                                        if clean_text:
                                            if deduplicate:
                                                if clean_text in seen_blocks: continue
                                                seen_blocks.add(clean_text)
                                            f_out.write(clean_text + "\n\n")
                                            bible_blocks += 1
                                            total_blocks += 1
                    except Exception as e:
                        print(f"   ❌ Erreur sur {filename}: {e}")
        print(f"   ✅ {bible_blocks} versets de la Bible ajoutés.")

        # 3. Charger Wikipedia
        if os.path.exists(wiki_path):
            print("📖 Chargement de Wikipedia Malagasy...")
            wiki_added = 0
            with open(wiki_path, 'r', encoding='utf-8') as f_wiki:
                # On traite par paragraphes
                for line in f_wiki:
                    clean_line = line.strip()
                    # On ignore les lignes vides et les lignes de titre
                    if not clean_line or clean_line.startswith("--- "):
                        continue
                    
                    if deduplicate:
                        if clean_line in seen_blocks:
                            continue
                        seen_blocks.add(clean_line)
                    
                    f_out.write(clean_line + "\n\n")
                    wiki_added += 1
                    total_blocks += 1
            print(f"   ✅ {wiki_added} paragraphes Wikipedia ajoutés.")
        else:
            print(f"   ⚠️ Wikipedia ({wiki_path}) non trouvé. Saut de l'étape.")

    print("======================================================================")
    print(f"🚀 CONSOLIDATION TERMINÉE !")
    print(f"📊 Total blocs UNIQUES dans le corpus : {total_blocks}")
    print(f"💾 Fichier sauvegardé : {output_path}")
    print("======================================================================")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Consolide les différentes sources de texte.')
    parser.add_argument('--lyrics', type=str, default='malagasy_lyrics_cleaned.txt', help='Lyrics nettoyés')
    parser.add_argument('--bible', type=str, default='../from_bible_json', help='Dossier Bible')
    parser.add_argument('--wiki', type=str, default='../malagasy_wikipedia_raw.txt', help='Wikipedia extrait')
    parser.add_argument('--output', type=str, default='malagasy_corpus_v2_final.txt', help='Fichier de sortie')
    parser.add_argument('--no-dedup', action='store_true', help='Désactive le dédoublonage')

    args = parser.parse_args()
    consolidate_corpus(args.lyrics, args.bible, args.wiki, args.output, deduplicate=not args.no_dedup)
