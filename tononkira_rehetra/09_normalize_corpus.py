import re
import argparse
import os

def normalize_corpus(input_path, output_path):
    print("======================================================================")
    print("🧹 NORMALISATION DU CORPUS (Pour Embeddings optimaux)")
    print(f"   Entrée : {input_path}")
    print(f"   Sortie : {output_path}")
    print("======================================================================")

    if not os.path.exists(input_path):
        print(f"❌ Erreur : {input_path} introuvable.")
        return

    with open(input_path, 'r', encoding='utf-8') as f_in, \
         open(output_path, 'w', encoding='utf-8') as f_out:
        
        line_count = 0
        for line in f_in:
            # 1. Mise en minuscule
            text = line.lower()
            
            # 2. Suppression de la ponctuation (garde les lettres malgaches)
            # On garde l'apostrophe typographique qui est fréquente en malgache
            text = re.sub(r"[^\w\s\u2019']", " ", text)
            
            # 3. Suppression des nombres
            text = re.sub(r"\d+", " ", text)
            
            # 4. Nettoyage des espaces multiples
            text = re.sub(r"\s+", " ", text).strip()
            
            if text:
                f_out.write(text + "\n")
                line_count += 1
            
            if line_count % 50000 == 0 and line_count > 0:
                print(f"   ⏳ {line_count} lignes traitées...")

    print("======================================================================")
    print(f"✅ NORMALISATION TERMINÉE !")
    print(f"📊 {line_count} lignes propres prêtes pour l'entraînement.")
    print("======================================================================")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Normalise le texte (minuscules, pas de ponctuation).')
    parser.add_argument('--input', type=str, default='malagasy_corpus_v1_fixed.txt', help='Corpus consolidé')
    parser.add_argument('--output', type=str, default='malagasy_corpus_normalized.txt', help='Corpus normalisé')

    args = parser.parse_args()
    normalize_corpus(args.input, args.output)
