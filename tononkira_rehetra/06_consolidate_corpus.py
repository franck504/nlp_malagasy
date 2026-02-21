import os
import json
import argparse

def consolidate_corpus(lyrics_path, bible_dir, output_path):
    print("======================================================================")
    print("📚 CONSOLIDATION DU CORPUS (Lyrics + Bible)")
    print(f"   Lyrics : {lyrics_path}")
    print(f"   Bible  : {bible_dir}")
    print(f"   Sortie : {output_path}")
    print("======================================================================")

    total_blocks = 0
    
    with open(output_path, 'w', encoding='utf-8') as f_out:
        # 1. Charger les Lyrics nettoyés
        if os.path.exists(lyrics_path):
            print("📖 Chargement des lyrics nettoyés...")
            with open(lyrics_path, 'r', encoding='utf-8') as f_in:
                for line in f_in:
                    f_out.write(line)
                    total_blocks += 1
            print(f"   ✅ {total_blocks} blocs de lyrics ajoutés.")
        else:
            print(f"   ⚠️ Attention : {lyrics_path} introuvable.")

        # 2. Charger la Bible
        bible_blocks = 0
        print("📖 Chargement de la Bible (Ancien et Nouveau Testament)...")
        
        for root_dir in ['old_testament', 'new_testament']:
            full_bible_path = os.path.join(bible_dir, root_dir)
            if not os.path.exists(full_bible_path):
                continue
                
            for filename in sorted(os.listdir(full_bible_path)):
                if filename.endswith('.json'):
                    file_path = os.path.join(full_bible_path, filename)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f_json:
                            data = json.load(f_json)
                            
                            # On parcourt les chapitres
                            for key, chapter in data.items():
                                # On ignore la clé 'meta' qui contient des stats
                                if key == "meta" or not isinstance(chapter, dict):
                                    continue
                                
                                for v_key, verse_text in chapter.items():
                                    # Sécurité : on ne prend que si c'est du texte (str)
                                    if isinstance(verse_text, str):
                                        clean_text = verse_text.strip()
                                        if clean_text:
                                            f_out.write(clean_text + "\n")
                                            bible_blocks += 1
                                            total_blocks += 1
                    except Exception as e:
                        print(f"   ❌ Erreur sur {filename}: {e}")

        print(f"   ✅ {bible_blocks} versets de la Bible ajoutés.")

    print("======================================================================")
    print(f"🚀 CONSOLIDATION TERMINÉE !")
    print(f"📊 Total blocs dans le corpus final : {total_blocks}")
    print(f"💾 Fichier sauvegardé : {output_path}")
    print("======================================================================")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Consolide les différentes sources de texte.')
    parser.add_argument('--lyrics', type=str, default='tononkira_rehetra/malagasy_lyrics_cleaned.txt', help='Chemin vers les lyrics nettoyés')
    parser.add_argument('--bible', type=str, default='from_bible_json', help='Dossier racine de la Bible JSON')
    parser.add_argument('--output', type=str, default='malagasy_corpus_v1.txt', help='Fichier de sortie consolidé')

    args = parser.parse_args()
    consolidate_corpus(args.lyrics, args.bible, args.output)
